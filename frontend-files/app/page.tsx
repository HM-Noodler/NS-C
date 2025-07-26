"use client";

import { Navigation } from "@/components/layout/navigation";
import { MetricsCards } from "@/components/dashboard/metrics-cards";
import { EscalationQueue } from "@/components/dashboard/escalation-queue";
import { TotalReceivables } from "@/components/dashboard/total-receivables";
import { RecentEmailActivity } from "@/components/dashboard/recent-email-activity";
import { FileUpload } from "@/components/dashboard/file-upload";
import { mockDashboardData } from "@/lib/api/services";

export default function Home() {
  const handleFileUpload = (file: File) => {
  };

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <main className="max-w-7xl mx-auto px-6 py-8 space-y-8">
        <EscalationQueue items={mockDashboardData.escalation_queue} />
        
        <div className="w-full px-6">
          <hr className="border-t" style={{ borderColor: "#E6E6E6" }} />
        </div>
        
        <FileUpload onFileUpload={handleFileUpload} />
        
        <MetricsCards metrics={mockDashboardData.metrics} />
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <TotalReceivables 
            receivables={mockDashboardData.receivables}
          />
          
          <RecentEmailActivity activities={mockDashboardData.recent_activity} />
        </div>
      </main>
    </div>
  );
}
