"use client";

import { useState } from "react";
import { usePathname } from "next/navigation";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { EscalationItem } from "@/types";

interface EscalationQueueProps {
  items: EscalationItem[];
}

export function EscalationQueue({ items }: EscalationQueueProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const pathname = usePathname();
  const isHomePage = pathname === "/";

  if (items.length === 0) {
    return null;
  }

  const firstItem = items[0];
  const additionalItems = items.slice(1);

  const handleSendEmail = (item: EscalationItem) => {
  };

  const handleViewEmailContent = (item: EscalationItem) => {
  };

  const renderEscalationItem = (item: EscalationItem) => (
    <div
      key={item.id}
      className="p-6"
      style={{ backgroundColor: "#FFFFFF" }}
    >
      {/* Top section: Company name and Send Email button */}
      <div className="flex items-start justify-between mb-3">
        <h3
          className="text-lg font-semibold mb-1"
          style={{
            fontFamily: "Poppins, system-ui, sans-serif",
            color: "#000000",
          }}
        >
          {item.company_name}
        </h3>
        <Button
          onClick={() => handleSendEmail(item)}
          variant="outline"
          className="h-8 px-4 text-sm font-medium bg-white"
          style={{
            fontFamily: "Poppins, system-ui, sans-serif",
            borderRadius: "0px 8px 0px 8px",
            borderColor: "#1E84FF",
          }}
        >
          Send Email
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth="1.5"
            stroke="#1E84FF"
            className="w-4 h-4 ml-2"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M6 12 3.269 3.125A59.769 59.769 0 0 1 21.485 12 59.768 59.768 0 0 1 3.27 20.875L5.999 12Zm0 0h7.5"
            />
          </svg>
        </Button>
      </div>

      {/* Middle section: Amount and queue info */}
      <div className="flex items-center space-x-4 mb-4">
        <span
          className="text-lg font-medium"
          style={{
            fontFamily: "Poppins, system-ui, sans-serif",
            color: "#000000",
          }}
        >
          ${item.amount.toLocaleString()} ({item.invoice_count} invoices)
        </span>
        <span
          className="text-sm bg-orange-100 px-2 py-1 rounded"
          style={{
            fontFamily: "Poppins, system-ui, sans-serif",
            color: "#636363",
          }}
        >
          {item.days_in_queue} days in queue
        </span>
      </div>

      {/* Bottom section: Description and View Email Content */}
      <div className="flex items-end justify-between">
        <p
          className="text-sm max-w-2xl flex-1 mr-4"
          style={{
            fontFamily: "Poppins, system-ui, sans-serif",
            color: "#636363",
          }}
        >
          Sent 2 emails with no response. Client may have changed email
          address or is actively avoiding contact. Recommend phone call or
          certified mail.
        </p>
        <Button
          variant="ghost"
          onClick={() => handleViewEmailContent(item)}
          className="h-8 px-3 py-1 text-sm font-medium text-blue-600 hover:text-blue-600 hover:bg-blue-100 whitespace-nowrap rounded-full"
          style={{ fontFamily: "Poppins, system-ui, sans-serif" }}
        >
          View Email Content
        </Button>
      </div>
    </div>
  );

  return (
    <Card
      className="w-full border-0 shadow-none"
      style={{ backgroundColor: "#F8F5F4" }}
    >
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke={isHomePage ? "#1E84FF" : "#6B7280"} className="w-6 h-6">
              <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 12h16.5m-16.5 3.75h16.5M3.75 19.5h16.5M5.625 4.5h12.75a1.875 1.875 0 0 1 0 3.75H5.625a1.875 1.875 0 0 1 0-3.75Z" />
            </svg>
            <h2
              className="text-xl font-semibold text-black"
              style={{ fontFamily: "Poppins, system-ui, sans-serif" }}
            >
              Email Escalation Queue
            </h2>
          </div>
          <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
            <span className="text-white text-sm font-semibold">{items.length}</span>
          </div>
        </div>
      </CardHeader>

      <CardContent className="pt-0 space-y-4">
        {/* First escalation item */}
        {renderEscalationItem(firstItem)}
        
        {/* Expand/Collapse button - only show if there are additional items */}
        {additionalItems.length > 0 && (
          <div className="flex justify-center">
            <Button
              variant="ghost"
              onClick={() => setIsExpanded(!isExpanded)}
              className="group h-10 px-4 text-sm font-medium text-gray-600 hover:text-gray-800 hover:bg-white rounded-full flex items-center space-x-2 transition-all duration-300 ease-in-out hover:px-6"
              style={{ fontFamily: "Poppins, system-ui, sans-serif" }}
            >
              <span className="transition-all duration-300 ease-in-out">
                {isExpanded ? 'Show Less' : `Show ${additionalItems.length} More`}
              </span>
              <div className="flex items-center space-x-1">
                <span className={`text-xs text-blue-600 font-semibold transition-all duration-300 ease-in-out ${
                  isExpanded 
                    ? 'opacity-0 -translate-x-2 max-w-0' 
                    : 'opacity-0 group-hover:opacity-100 group-hover:translate-x-0 max-w-0 group-hover:max-w-[60px] translate-x-2'
                } overflow-hidden whitespace-nowrap`}>
                  urgent
                </span>
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth="1.5"
                  stroke="currentColor"
                  className={`w-4 h-4 transition-all duration-500 ease-in-out group-hover:scale-110 ${isExpanded ? 'rotate-180' : ''}`}
                >
                  <path strokeLinecap="round" strokeLinejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" />
                </svg>
              </div>
            </Button>
          </div>
        )}
        
        {/* Additional escalation items - shown when expanded */}
        <div className={`transition-all duration-500 ease-in-out overflow-hidden ${
          isExpanded ? 'max-h-[2000px] opacity-100' : 'max-h-0 opacity-0'
        }`}>
          <div className="space-y-4">
            {additionalItems.map((item) => renderEscalationItem(item))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
