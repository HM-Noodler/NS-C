import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { EmailActivity } from "@/types";

interface RecentEmailActivityProps {
  activities: EmailActivity[];
}

export function RecentEmailActivity({ activities }: RecentEmailActivityProps) {
  const conciergeEmails = activities.filter(a => a.email_type === 'concierge').length;
  const totalActivity = activities.length;
  const conciergePercentage = totalActivity > 0 ? Math.round((conciergeEmails / totalActivity) * 100) : 0;

  return (
    <Card
      className="border-0 shadow-none"
      style={{ backgroundColor: "#F8F5F4" }}
    >
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <CardTitle
            className="text-xl font-semibold text-black"
            style={{ fontFamily: "Poppins, system-ui, sans-serif" }}
          >
            Recent Email Activity
          </CardTitle>
          {activities.length > 0 && (
            <Button
              variant="ghost"
              className="text-blue-600 hover:text-blue-600 hover:bg-blue-100 px-3 py-1 h-auto rounded-full"
              style={{ fontFamily: "Poppins, system-ui, sans-serif" }}
            >
              View All
            </Button>
          )}
        </div>
        <p
          className="text-sm text-gray-600"
          style={{ fontFamily: "Poppins, system-ui, sans-serif" }}
        >
          Latest concierge communications
        </p>
      </CardHeader>

      <CardContent className="pt-0">
        {activities.length === 0 ? (
          <div className="text-center py-12">
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              fill="none" 
              viewBox="0 0 24 24" 
              strokeWidth="1.5" 
              stroke="#9CA3AF" 
              className="w-12 h-12 mx-auto mb-4"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                d="M21.75 6.75v10.5a2.25 2.25 0 0 1-2.25 2.25h-15a2.25 2.25 0 0 1-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0 0 19.5 4.5h-15a2.25 2.25 0 0 0-2.25 2.25m19.5 0v.243a2.25 2.25 0 0 1-1.07 1.916l-7.5 4.615a2.25 2.25 0 0 1-2.36 0L3.32 8.91a2.25 2.25 0 0 1-1.07-1.916V6.75" 
              />
            </svg>
            <p 
              className="text-gray-500 text-lg mb-2" 
              style={{ fontFamily: "Poppins, system-ui, sans-serif" }}
            >
              No Email Activity Yet
            </p>
            <p 
              className="text-gray-400 text-sm" 
              style={{ fontFamily: "Poppins, system-ui, sans-serif" }}
            >
              Email activity will appear here after you upload CSV data and send escalation emails.
            </p>
          </div>
        ) : (
          <>
            <div className="space-y-4 mb-6">
              {activities.slice(0, 5).map((activity) => (
                <div
                  key={activity.id}
                  className="flex items-center justify-between p-3 bg-white/50 rounded-lg"
                >
                  <div className="flex items-center space-x-3">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      strokeWidth="1.5"
                      stroke="#1E84FF"
                      className="w-6 h-6"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M21.75 6.75v10.5a2.25 2.25 0 0 1-2.25 2.25h-15a2.25 2.25 0 0 1-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0 0 19.5 4.5h-15a2.25 2.25 0 0 0-2.25 2.25m19.5 0v.243a2.25 2.25 0 0 1-1.07 1.916l-7.5 4.615a2.25 2.25 0 0 1-2.36 0L3.32 8.91a2.25 2.25 0 0 1-1.07-1.916V6.75"
                      />
                    </svg>

                    <div>
                      <h4
                        className="font-medium text-black"
                        style={{ fontFamily: "Poppins, system-ui, sans-serif" }}
                      >
                        {activity.company_name}
                      </h4>
                      <div className="flex items-center space-x-2">
                        <span
                          className="text-sm text-gray-600"
                          style={{ fontFamily: "Poppins, system-ui, sans-serif" }}
                        >
                          {activity.email_type} email • {activity.sent_date}
                        </span>
                        <span
                          className={`text-xs px-2 py-1 rounded-full ${
                            activity.status === 'sent' ? 'bg-blue-100 text-blue-700' :
                            activity.status === 'opened' ? 'bg-green-100 text-green-700' :
                            activity.status === 'responded' ? 'bg-purple-100 text-purple-700' :
                            'bg-red-100 text-red-700'
                          }`}
                          style={{ fontFamily: "Poppins, system-ui, sans-serif" }}
                        >
                          {activity.status}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="text-right">
                    <div
                      className="font-semibold text-black"
                      style={{ fontFamily: "Poppins, system-ui, sans-serif" }}
                    >
                      ${activity.amount.toLocaleString()}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Bottom Summary Metrics */}
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center p-4 bg-white rounded-lg">
                <div
                  className="text-2xl font-bold text-black mb-1"
                  style={{ fontFamily: "Poppins, system-ui, sans-serif" }}
                >
                  {conciergeEmails}
                </div>
                <div
                  className="text-sm font-medium text-gray-700"
                  style={{ fontFamily: "Poppins, system-ui, sans-serif" }}
                >
                  Concierge Emails
                </div>
                <div
                  className="text-xs text-gray-600"
                  style={{ fontFamily: "Poppins, system-ui, sans-serif" }}
                >
                  Automated
                </div>
                <div
                  className="text-xs text-gray-600"
                  style={{ fontFamily: "Poppins, system-ui, sans-serif" }}
                >
                  {conciergePercentage}% of total
                </div>
              </div>

              <div className="text-center p-4 bg-white rounded-lg">
                <div
                  className="text-2xl font-bold text-black mb-1"
                  style={{ fontFamily: "Poppins, system-ui, sans-serif" }}
                >
                  {totalActivity}
                </div>
                <div
                  className="text-sm font-medium text-gray-700"
                  style={{ fontFamily: "Poppins, system-ui, sans-serif" }}
                >
                  Total Activity
                </div>
                <div
                  className="text-xs text-gray-600"
                  style={{ fontFamily: "Poppins, system-ui, sans-serif" }}
                >
                  Communications
                </div>
                <div
                  className="text-xs text-gray-600"
                  style={{ fontFamily: "Poppins, system-ui, sans-serif" }}
                >
                  Recent emails
                </div>
              </div>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}
