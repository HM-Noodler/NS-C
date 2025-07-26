import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ReceivablesData } from "@/types";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface TotalReceivablesProps {
  receivables: ReceivablesData;
}

export function TotalReceivables({ receivables }: TotalReceivablesProps) {
  // Sample time series data - this would come from your API
  const timeSeriesData = [
    { month: 'Jan', paid: 95000, outstanding: 165000 },
    { month: 'Feb', paid: 102000, outstanding: 158000 },
    { month: 'Mar', paid: 108000, outstanding: 152000 },
    { month: 'Apr', paid: 115000, outstanding: 145000 },
    { month: 'May', paid: 118000, outstanding: 150000 },
    { month: 'Jun', paid: receivables.paid_collections, outstanding: receivables.outstanding_receivables }
  ];

  return (
    <Card 
      className="border-0 shadow-none"
      style={{ backgroundColor: '#F8F5F4' }}
    >
      <CardHeader className="pb-4">
        <CardTitle 
          className="text-xl font-semibold text-black"
          style={{ fontFamily: 'Poppins, system-ui, sans-serif' }}
        >
          Total Receivables
        </CardTitle>
        <p 
          className="text-sm text-gray-600"
          style={{ fontFamily: 'Poppins, system-ui, sans-serif' }}
        >
          Collections performance overview
        </p>
      </CardHeader>
      
      <CardContent className="pt-0">
        {/* Time Series Chart */}
        <div className="h-48 mb-6">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={timeSeriesData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis 
                dataKey="month" 
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 12, fill: '#6B7280' }}
              />
              <YAxis 
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 12, fill: '#6B7280' }}
                tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
              />
              <Tooltip 
                formatter={(value: number) => [`$${value.toLocaleString()}`, '']}
                labelStyle={{ color: '#374151' }}
                contentStyle={{ 
                  backgroundColor: 'white', 
                  border: '1px solid #E5E7EB',
                  borderRadius: '6px'
                }}
              />
              <Line 
                type="monotone" 
                dataKey="paid" 
                stroke="#2DB294" 
                strokeWidth={2}
                dot={{ fill: '#2DB294', strokeWidth: 2, r: 4 }}
                name="Paid"
              />
              <Line 
                type="monotone" 
                dataKey="outstanding" 
                stroke="#F2BE7C" 
                strokeWidth={2}
                dot={{ fill: '#F2BE7C', strokeWidth: 2, r: 4 }}
                name="Outstanding"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
        
        {/* Metrics */}
        <div className="grid grid-cols-2 gap-4">
          <div className="text-center p-4 bg-white rounded-lg">
            <div
              className="text-2xl font-bold mb-1"
              style={{ fontFamily: "Poppins, system-ui, sans-serif", color: "#2DB294" }}
            >
              ${receivables.paid_collections.toLocaleString()}
            </div>
            <div
              className="text-sm font-medium"
              style={{ fontFamily: "Poppins, system-ui, sans-serif", color: "#2DB294" }}
            >
              Paid
            </div>
            <div
              className="text-xs text-gray-600"
              style={{ fontFamily: "Poppins, system-ui, sans-serif" }}
            >
              Collections
            </div>
            <div
              className="text-xs text-gray-600"
              style={{ fontFamily: "Poppins, system-ui, sans-serif" }}
            >
              {receivables.paid_percentage}% of total
            </div>
          </div>

          <div className="text-center p-4 bg-white rounded-lg">
            <div
              className="text-2xl font-bold mb-1"
              style={{ fontFamily: "Poppins, system-ui, sans-serif", color: "#F2BE7C" }}
            >
              ${receivables.outstanding_receivables.toLocaleString()}
            </div>
            <div
              className="text-sm font-medium"
              style={{ fontFamily: "Poppins, system-ui, sans-serif", color: "#F2BE7C" }}
            >
              Outstanding
            </div>
            <div
              className="text-xs text-gray-600"
              style={{ fontFamily: "Poppins, system-ui, sans-serif" }}
            >
              Receivables
            </div>
            <div
              className="text-xs text-gray-600"
              style={{ fontFamily: "Poppins, system-ui, sans-serif" }}
            >
              {receivables.outstanding_percentage}% of total
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}