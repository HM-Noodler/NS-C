import Image from "next/image";
import { Card } from "@/components/ui/card";
import { CollectionMetrics } from "@/types";
import { useState } from "react";

interface MetricCardProps {
  title: string;
  value: number;
  subtitle?: string;
  backgroundColor: string;
  accentColor: string;
  icon: string;
  amount?: string;
  keyword: string;
}

function MetricCard({
  title,
  value,
  subtitle,
  backgroundColor,
  accentColor,
  icon,
  amount,
  keyword,
}: MetricCardProps) {
  const [isHovered, setIsHovered] = useState(false);
  return (
    <Card
      className="border-2 border-transparent h-full min-h-[200px] p-6 transition-all duration-200 cursor-pointer hover:border-current shadow-none"
      style={{
        backgroundColor,
        borderRadius: "0px 20px 0px 20px",
        borderColor: "transparent",
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.borderColor = accentColor;
        setIsHovered(true);
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.borderColor = "transparent";
        setIsHovered(false);
      }}
    >
      <div className="h-full flex flex-col justify-between">
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-3">
            <Image
              src={icon}
              alt={`${title} icon`}
              width={48}
              height={48}
              className="w-12 h-12 rounded-full"
            />
            <div>
              <h3
                className="text-lg font-medium text-black"
                style={{ fontFamily: "Poppins, system-ui, sans-serif" }}
              >
                {title}
              </h3>
              {subtitle && (
                <p
                  className="text-xs opacity-75 text-black"
                  style={{ fontFamily: "Poppins, system-ui, sans-serif" }}
                >
                  {subtitle}
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Footer with large number */}
        <div className="flex items-end justify-between mt-4">
          <div className="flex items-center relative">
            <div className="relative">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth="1.5"
                stroke="currentColor"
                className={`w-6 h-6 transition-all duration-300 ${isHovered ? 'opacity-0 scale-95' : 'opacity-100 scale-100'}`}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="m8.25 4.5 7.5 7.5-7.5 7.5"
                />
              </svg>
              <div 
                className={`absolute inset-0 flex items-center justify-center transition-all duration-300 ${isHovered ? 'opacity-100 scale-100' : 'opacity-0 scale-95'}`}
                style={{
                  fontSize: '14px',
                  fontWeight: '600',
                  color: accentColor,
                  fontFamily: 'Poppins, system-ui, sans-serif',
                  letterSpacing: '0.5px',
                  transform: isHovered ? 'scale(1)' : 'scale(0.8)',
                }}
              >
                {keyword}
              </div>
            </div>
          </div>
          <div className="text-right">
            {amount && (
              <div
                style={{
                  fontSize: "24px",
                  fontWeight: "500",
                  color: accentColor,
                  lineHeight: "1",
                  fontFamily: "Poppins, system-ui, sans-serif",
                  marginBottom: "8px",
                }}
              >
                {amount}
              </div>
            )}
            <div
              style={{
                fontSize: "96px",
                fontWeight: "300",
                color: accentColor,
                lineHeight: "1",
                fontFamily: "Poppins, system-ui, sans-serif",
              }}
            >
              {value}
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
}

interface MetricsCardsProps {
  metrics: CollectionMetrics;
}

export function MetricsCards({ metrics }: MetricsCardsProps) {
  const cards = [
    {
      title: "Successful Collections",
      value: metrics.successful_collections,
      backgroundColor: "#A5FFEB", // Light mint green
      accentColor: "#29DFB6", // Mint green
      icon: "/Successful Collections.png",
      amount: `$${metrics.successful_collections_amount.toLocaleString()}`,
      keyword: "VIEW",
    },
    {
      title: "Active Email Campaigns",
      value: metrics.active_email_campaigns,
      subtitle: `Total value: $${metrics.active_email_campaigns_amount.toLocaleString()}`,
      backgroundColor: "#FFE4C2", // Light orange
      accentColor: "#F2BE7C", // Orange
      icon: "/Active Emails.png",
      keyword: "TRACK",
    },
    {
      title: "Email Escalation Queue",
      value: metrics.email_escalation_queue,
      backgroundColor: "#FFDBF5", // Light pink
      accentColor: "#DB97C8", // Pink
      icon: "/Email Escalation Queue.png",
      amount: `$${metrics.email_escalation_queue_amount.toLocaleString()}`,
      keyword: "HANDLE",
    },
    {
      title: "Total Email Communications",
      value: metrics.total_email_communications,
      subtitle: "Recent activity",
      backgroundColor: "#E5D9FF", // Light purple
      accentColor: "#8677A5", // Purple
      icon: "/Total Email Communication.png",
      keyword: "SEND",
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
      {cards.map((card, index) => (
        <MetricCard key={index} {...card} />
      ))}
    </div>
  );
}