import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { EmailActivity } from "@/types";

interface RecentActivityProps {
  activities: EmailActivity[];
}

function getStatusColor(status: EmailActivity['status']) {
  switch (status) {
    case 'sent':
      return 'bg-blue-100 text-blue-800';
    case 'opened':
      return 'bg-green-100 text-green-800';
    case 'responded':
      return 'bg-green-100 text-green-800';
    case 'bounced':
      return 'bg-red-100 text-red-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
}

function getEmailTypeIcon(type: EmailActivity['email_type']) {
  return type === 'concierge' ? '🤖' : '✉️';
}

export function RecentActivity({ activities }: RecentActivityProps) {
  return (
    <Card className="w-full shadow-sm border border-gray-200">
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <CardTitle 
            className="text-xl font-semibold text-black"
            style={{ fontFamily: 'Poppins, system-ui, sans-serif' }}
          >
            Recent Email Activity
          </CardTitle>
          <Button 
            variant="ghost" 
            className="text-blue-600 hover:text-blue-600 hover:bg-blue-100 px-3 py-1 h-auto rounded-full"
            style={{ fontFamily: 'Poppins, system-ui, sans-serif' }}
          >
            View All
          </Button>
        </div>
        <p 
          className="text-sm text-gray-600"
          style={{ fontFamily: 'Poppins, system-ui, sans-serif' }}
        >
          Latest concierge communications
        </p>
      </CardHeader>
      
      <CardContent className="pt-0">
        <div className="space-y-4">
          {activities.map((activity) => (
            <div 
              key={activity.id} 
              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                  <span className="text-sm">
                    {getEmailTypeIcon(activity.email_type)}
                  </span>
                </div>
                
                <div>
                  <h4 
                    className="font-medium text-black"
                    style={{ fontFamily: 'Poppins, system-ui, sans-serif' }}
                  >
                    {activity.company_name}
                  </h4>
                  <div className="flex items-center space-x-2">
                    <span 
                      className="text-sm text-gray-600"
                      style={{ fontFamily: 'Poppins, system-ui, sans-serif' }}
                    >
                      {activity.email_type} email • {activity.sent_date}
                    </span>
                    <Badge 
                      className={`text-xs ${getStatusColor(activity.status)}`}
                    >
                      {activity.status}
                    </Badge>
                  </div>
                </div>
              </div>
              
              <div className="text-right">
                <div 
                  className="font-semibold text-black"
                  style={{ fontFamily: 'Poppins, system-ui, sans-serif' }}
                >
                  ${activity.amount.toLocaleString()}
                </div>
                <div className="flex items-center space-x-1">
                  <div 
                    className={`w-2 h-2 rounded-full ${
                      activity.email_type === 'concierge' ? 'bg-blue-500' : 'bg-gray-400'
                    }`}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}