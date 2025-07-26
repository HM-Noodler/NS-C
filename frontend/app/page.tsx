"use client";

import { useState, useEffect } from "react";
import { Navigation } from "@/components/layout/navigation";
import { MetricsCards } from "@/components/dashboard/metrics-cards";
import { EscalationQueue } from "@/components/dashboard/escalation-queue";
import { TotalReceivables } from "@/components/dashboard/total-receivables";
import { RecentEmailActivity } from "@/components/dashboard/recent-email-activity";
import { FileUpload } from "@/components/dashboard/file-upload";
import { EscalationItem, CollectionMetrics, ReceivablesData, EmailActivity } from "@/types";

export default function Home() {
  const [escalationQueue, setEscalationQueue] = useState<EscalationItem[]>([]);
  const [metrics, setMetrics] = useState<CollectionMetrics>({
    successful_collections: 0,
    successful_collections_amount: 0,
    active_email_campaigns: 0,
    active_email_campaigns_amount: 0,
    email_escalation_queue: 0,
    email_escalation_queue_amount: 0,
    total_email_communications: 0,
  });
  const [receivables, setReceivables] = useState<ReceivablesData>({
    paid_collections: 0,
    paid_percentage: 0,
    outstanding_receivables: 0,
    outstanding_percentage: 0,
    total_amount: 0,
  });
  const [recentActivity, setRecentActivity] = useState<EmailActivity[]>([]);
  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        // Test basic fetch first
        const response = await fetch('http://localhost:8080/api/v1/dashboard/metrics');
        if (response.ok) {
          const metricsData = await response.json();
          setMetrics(metricsData);
        }

        const queueResponse = await fetch('http://localhost:8080/api/v1/dashboard/escalation-queue');
        if (queueResponse.ok) {
          const queueData = await queueResponse.json();
          setEscalationQueue(queueData);
        }

        const receivablesResponse = await fetch('http://localhost:8080/api/v1/dashboard/receivables');
        if (receivablesResponse.ok) {
          const receivablesData = await receivablesResponse.json();
          setReceivables(receivablesData);
        }

        const activityResponse = await fetch('http://localhost:8080/api/v1/dashboard/recent-activity');
        if (activityResponse.ok) {
          const activityData = await activityResponse.json();
          setRecentActivity(activityData);
        }
      } catch (error) {
        console.error('Failed to load dashboard data:', error);
      }
    };

    loadDashboardData();
  }, []);

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <main className="max-w-7xl mx-auto px-6 py-8 space-y-8">
        <EscalationQueue items={escalationQueue} />
        
        <div className="w-full px-6">
          <hr className="border-t" style={{ borderColor: "#E6E6E6" }} />
        </div>
        
        <FileUpload />
        
        <MetricsCards metrics={metrics} />
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <TotalReceivables receivables={receivables} />
          <RecentEmailActivity activities={recentActivity} />
        </div>
      </main>
    </div>
  );
}