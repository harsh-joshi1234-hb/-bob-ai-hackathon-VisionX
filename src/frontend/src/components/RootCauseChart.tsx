import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import type { RootCause } from '../api/lotsApi';

export function RootCauseChart({ data }: { data: RootCause[] }) {
  if (!data || data.length === 0) {
    return <div className="text-sm text-muted-foreground p-4">No root cause data available.</div>;
  }

  // Format data for Recharts
  const chartData = data.map(item => ({
    name: item.feature.replace('feature_', 'F'),
    value: item.contribution,
    direction: item.direction
  })).reverse(); // Reverse so highest is at top in horizontal chart

  return (
    <div className="h-[300px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          layout="vertical"
          data={chartData}
          margin={{
            top: 5,
            right: 30,
            left: 40,
            bottom: 5,
          }}
        >
          <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} stroke="hsl(var(--border))" />
          <XAxis type="number" stroke="hsl(var(--muted-foreground))" fontSize={12} tickLine={false} axisLine={false} />
          <YAxis dataKey="name" type="category" stroke="hsl(var(--muted-foreground))" fontSize={12} tickLine={false} axisLine={false} />
          <Tooltip 
            cursor={{fill: 'hsl(var(--secondary))'}}
            contentStyle={{ backgroundColor: 'hsl(var(--card))', borderColor: 'hsl(var(--border))', borderRadius: '6px' }}
            itemStyle={{ color: 'hsl(var(--foreground))' }}
          />
          <Bar dataKey="value" radius={[0, 4, 4, 0]}>
            {chartData.map((entry, index) => (
              <Cell 
                key={`cell-${index}`} 
                fill={entry.direction === 'increases_risk' ? 'hsl(var(--destructive))' : 'hsl(var(--primary))'} 
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
