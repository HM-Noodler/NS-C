import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ReceivablesData, ActivitySummary } from "@/types";

interface ReceivablesSectionProps {
  receivables: ReceivablesData;
  activitySummary: ActivitySummary;
}

export function ReceivablesSection({
  receivables,
  activitySummary,
}: ReceivablesSectionProps) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Total Receivables Chart */}
      <Card className="">
        <CardHeader className="pb-4">
          <CardTitle
            className="text-xl font-semibold text-black"
            style={{ fontFamily: "Poppins, system-ui, sans-serif" }}
          >
            Total Receivables
          </CardTitle>
          <p
            className="text-sm text-gray-600"
            style={{ fontFamily: "Poppins, system-ui, sans-serif" }}
          >
            Collections performance overview
          </p>
        </CardHeader>

        <CardContent className="pt-0">
          {/* Chart Placeholder */}
          <div className="h-48 bg-gray-100 rounded-lg flex items-center justify-center mb-6">
            <p
              className="text-gray-500 text-lg font-medium"
              style={{ fontFamily: "Poppins, system-ui, sans-serif" }}
            >
              Chart goes here
            </p>
          </div>

          {/* Metrics */}
          <div className="grid grid-cols-1 gap-4">
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div
                className="text-2xl font-bold text-green-700 mb-1"
                style={{ fontFamily: "Poppins, system-ui, sans-serif" }}
              >
                ${receivables.paid_collections.toLocaleString()}
              </div>
              <div
                className="text-sm font-medium text-green-600"
                style={{ fontFamily: "Poppins, system-ui, sans-serif" }}
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

            <div className="text-center p-4 bg-orange-50 rounded-lg">
              <div
                className="text-2xl font-bold text-orange-700 mb-3"
                style={{ fontFamily: "Poppins, system-ui, sans-serif" }}
              >
                ${receivables.outstanding_receivables.toLocaleString()}
              </div>
              <div
                className="text-sm font-medium text-orange-600"
                style={{ fontFamily: "Poppins, system-ui, sans-serif" }}
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

      {/* Activity Summary - Positioned to match design layout */}
      <div className="space-y-6">
        {/* This empty space maintains the layout from the design */}
        <div className="h-32"></div>

        {/* Bottom metrics row */}
        <div className="grid grid-cols-2 gap-4">
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <div
              className="text-3xl font-bold text-black mb-1"
              style={{ fontFamily: "Poppins, system-ui, sans-serif" }}
            >
              {activitySummary.concierge_emails}
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
              {activitySummary.concierge_emails_percentage}% of total
            </div>
          </div>

          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div
              className="text-3xl font-bold text-black mb-1"
              style={{ fontFamily: "Poppins, system-ui, sans-serif" }}
            >
              {activitySummary.total_activity}
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
              Recent emails: {activitySummary.recent_emails}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
