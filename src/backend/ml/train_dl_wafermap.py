import os
import numpy as np
import pandas as pd
import sys
try:
    import pandas.core.indexes
    sys.modules['pandas.indexes'] = pandas.core.indexes
except Exception:
    pass
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt
import cv2

# ==========================================
# CONFIGURATION
# ==========================================
# IMPORTANT: Update this path to where your LSWMD.pkl is located
DATASET_PATH = r"c:/Users/harsh/Downloads/LSWMD.pkl/LSWMD.pkl"
IMAGE_SIZE = 64
BATCH_SIZE = 64
EPOCHS = 10
LEARNING_RATE = 0.001
MODEL_SAVE_PATH = "wafermap_dl_model.pth"

# ==========================================
# 1. PYTORCH DATASET
# ==========================================
class WaferMapDataset(Dataset):
    def __init__(self, X, y, img_size=64):
        self.X = X
        self.y = y
        self.img_size = img_size
        
    def __len__(self):
        return len(self.X)
        
    def __getitem__(self, idx):
        # The wafer map is a 2D numpy array
        wafer_img = self.X.iloc[idx]
        
        # Resize to a fixed size using OpenCV
        # cv2.resize expects (width, height)
        # Using nearest neighbor interpolation because pixel values are discrete (0, 1, 2)
        wafer_resized = cv2.resize(
            wafer_img.astype(np.float32), 
            (self.img_size, self.img_size), 
            interpolation=cv2.INTER_NEAREST
        )
        
        # Scale values roughly to [0, 1] (originally 0, 1, 2)
        wafer_resized = wafer_resized / 2.0
        
        # Add channel dimension: (1, img_size, img_size)
        tensor_x = torch.tensor(wafer_resized, dtype=torch.float32).unsqueeze(0)
        tensor_y = torch.tensor(self.y.iloc[idx], dtype=torch.long)
        
        return tensor_x, tensor_y

# ==========================================
# 2. CNN ARCHITECTURE
# ==========================================
class WaferMapCNN(nn.Module):
    def __init__(self, num_classes=9):
        super(WaferMapCNN, self).__init__()
        
        # Input shape: (Batch, 1, 64, 64)
        self.features = nn.Sequential(
            nn.Conv2d(1, 16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2), # Output: 16x32x32
            
            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2), # Output: 32x16x16
            
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2)  # Output: 64x8x8
        )
        
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 8 * 8, 256),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(256, num_classes)
        )
        
    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x

# ==========================================
# 3. DATA LOADING AND PREPROCESSING
# ==========================================
def load_and_preprocess_data():
    if not os.path.exists(DATASET_PATH):
        print(f"Error: Dataset not found at {DATASET_PATH}")
        print("Please update DATASET_PATH to the correct location of LSWMD.pkl")
        return None, None
        
    print(f"Loading dataset from {DATASET_PATH}...")
    import pickle
    with open(DATASET_PATH, 'rb') as f:
        df = pickle.load(f, encoding='latin1')
    
    print("Preprocessing labels...")
    mapping_type = {
        'Center': 0, 'Donut': 1, 'Edge-Loc': 2, 'Edge-Ring': 3, 
        'Loc': 4, 'Random': 5, 'Scratch': 6, 'Near-full': 7, 'none': 8
    }
    
    # Extract failure types from the nested structure [[type]]
    def get_failure_type(val):
        if len(val) > 0 and len(val[0]) > 0:
            return mapping_type.get(val[0][0], -1)
        return -1
        
    df['failureNum'] = df.failureType.apply(get_failure_type)
    
    # Filter to keep only labeled data (0 to 8)
    df_withlabel = df[(df['failureNum'] >= 0) & (df['failureNum'] <= 8)].copy()
    df_withlabel.reset_index(drop=True, inplace=True)
    
    print(f"Total labeled wafers to train on: {len(df_withlabel)}")
    return df_withlabel['waferMap'], df_withlabel['failureNum']

# ==========================================
# 4. TRAINING LOOP
# ==========================================
def train_model():
    X, y = load_and_preprocess_data()
    if X is None:
        return
        
    # Split data into training and validation
    print("Splitting data...")
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
    
    train_dataset = WaferMapDataset(X_train, y_train, img_size=IMAGE_SIZE)
    val_dataset = WaferMapDataset(X_val, y_val, img_size=IMAGE_SIZE)
    
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)
    
    # Initialize model, loss function, and optimizer
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training on device: {device}")
    
    model = WaferMapCNN(num_classes=9).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    
    # Best model tracking
    best_val_acc = 0.0
    
    history = {'train_loss': [], 'train_acc': [], 'val_loss': [], 'val_acc': []}
    
    print("Starting training...")
    for epoch in range(EPOCHS):
        # Training Phase
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            
            optimizer.zero_grad()
            
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            
        train_acc = 100 * correct / total
        train_loss = running_loss / len(train_loader)
        
        # Validation Phase
        model.eval()
        val_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                
                val_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
                
        val_acc = 100 * correct / total
        val_loss = val_loss / len(val_loader)
        
        history['train_loss'].append(train_loss)
        history['train_acc'].append(train_acc)
        history['val_loss'].append(val_loss)
        history['val_acc'].append(val_acc)
        
        print(f"Epoch [{epoch+1}/{EPOCHS}] "
              f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}% | "
              f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%")
              
        # Save the best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), MODEL_SAVE_PATH)
            print(f"  -> Best model saved to {MODEL_SAVE_PATH}")

    # Plot Accuracy and Loss Curves
    print("Saving accuracy and loss curves...")
    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 2, 1)
    plt.plot(history['train_acc'], label='Train Acc')
    plt.plot(history['val_acc'], label='Val Acc')
    plt.title('Accuracy over Epochs')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy (%)')
    plt.legend()
    
    plt.subplot(1, 2, 2)
    plt.plot(history['train_loss'], label='Train Loss')
    plt.plot(history['val_loss'], label='Val Loss')
    plt.title('Loss over Epochs')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('accuracy_loss_curve.png')
    plt.close()

    # Load best model for Confusion Matrix
    print("Generating confusion matrix...")
    model.load_state_dict(torch.load(MODEL_SAVE_PATH))
    model.eval()
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for inputs, labels in val_loader:
            inputs = inputs.to(device)
            outputs = model(inputs)
            _, predicted = torch.max(outputs.data, 1)
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.numpy())
            
    cm = confusion_matrix(all_labels, all_preds)
    
    # Plot using matplotlib/sklearn directly instead of seaborn
    fig, ax = plt.subplots(figsize=(10, 8))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, 
                                  display_labels=['Center', 'Donut', 'Edge-Loc', 'Edge-Ring', 
                                                  'Loc', 'Random', 'Scratch', 'Near-full', 'none'])
    disp.plot(cmap='Blues', ax=ax, xticks_rotation=45)
    
    plt.title('Confusion Matrix')
    plt.tight_layout()
    plt.savefig('confusion_matrix.png')
    plt.close()
    
    print("Training complete! Model and plots saved.")

if __name__ == "__main__":
    train_model()
