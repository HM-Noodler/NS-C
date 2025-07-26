"use client";

import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Navigation } from "@/components/layout/navigation";
import { EmailWorkflowModal } from "@/components/dashboard/email-workflow-modal";
import { EmailCollectionWorkflow } from "@/types";

// Helper function to calculate days overdue
function calculateDaysOverdue(invoiceDate: string): number {
  const today = new Date();
  const invoice = new Date(invoiceDate);
  const diffTime = today.getTime() - invoice.getTime();
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
}

// Helper function to determine email stage based on days overdue
function getEmailStageFromDays(daysOverdue: number): string {
  if (daysOverdue <= 30) return "First Contact";
  if (daysOverdue <= 60) return "Friendly";
  if (daysOverdue <= 90) return "Urgent";
  if (daysOverdue <= 120) return "Final Notice";
  return "Escalated";
}

const mockActiveCollections = [
  {
    id: "1",
    client: "Hudson Jeans",
    invoices: "2 invoices\nFW-2024-1847, FW-2024-1923",
    totalAmount: 43250,
    invoiceDate: "2024-03-15",     lastContact: "Payment plan discussion needed\nJul 23, 2025 12:30 AM",
    emailCount: 2,
  },
  {
    id: "2", 
    client: "Metro Textiles",
    invoices: "1 invoice\nFW-2024-2156",
    totalAmount: 12300,
    invoiceDate: "2025-07-10",     lastContact: "First payment reminder sent\nJul 23, 2025 12:30 AM",
    emailCount: 1,
  },
  {
    id: "3",
    client: "Fashion Forward LLC",
    invoices: "1 invoice\nFW-2024-2089",
    totalAmount: 8750,
    invoiceDate: "2025-05-20",     lastContact: "Follow-up email sent\nJul 24, 2025 12:30 AM",
    emailCount: 2,
  },
  {
    id: "4",
    client: "TechStart Inc",
    invoices: "1 invoice\nFW-2024-2201",
    totalAmount: 5200,
    invoiceDate: "2025-07-20",     lastContact: "Invoice recently became overdue\nJul 25, 2025 12:30 AM",
    emailCount: 0,
  },
  {
    id: "5",
    client: "Global Solutions",
    invoices: "1 invoice\nFW-2024-2178",
    totalAmount: 9800,
    invoiceDate: "2025-07-05",     lastContact: "First payment reminder sent\nJul 22, 2025 12:30 AM",
    emailCount: 1,
  },
  {
    id: "6",
    client: "Coastal Apparel Inc.",
    invoices: "1 invoice\nFW-2024-2202",
    totalAmount: 8900,
    invoiceDate: "2025-06-10",     lastContact: "First reminder sent\nJul 23, 2025 12:30 AM",
    emailCount: 1,
  },
  {
    id: "7",
    client: "Trendy Boutique",
    invoices: "1 invoice\nFW-2024-2207",
    totalAmount: 6700,
    invoiceDate: "2025-05-10",     lastContact: "First reminder sent\nJul 23, 2025 12:30 AM",
    emailCount: 1,
  },
  {
    id: "8",
    client: "Modern Apparel Group",
    invoices: "1 invoice\nFW-2024-2211",
    totalAmount: 16400,
    invoiceDate: "2025-04-20",     lastContact: "Final notice issued\nJul 21, 2025 12:30 AM",
    emailCount: 1,
  },
  {
    id: "9",
    client: "Fashion District LLC",
    invoices: "1 invoice\nFW-2024-2217",
    totalAmount: 14200,
    invoiceDate: "2025-06-25",     lastContact: "First reminder sent\nJul 22, 2025 12:30 AM",
    emailCount: 1,
  },
  {
    id: "10",
    client: "Urban Style Co.",
    invoices: "1 invoice\nFW-2024-2220",
    totalAmount: 7800,
    invoiceDate: "2025-05-15",     lastContact: "Second reminder sent\nJul 20, 2025 12:30 AM",
    emailCount: 2,
  },
  {
    id: "11",
    client: "Luxury Fashion House",
    invoices: "3 invoices\nFW-2024-2225, FW-2024-2226, FW-2024-2227",
    totalAmount: 25900,
    invoiceDate: "2024-02-15", // 160+ days overdue
    lastContact: "Legal notice prepared\nJul 19, 2025 12:30 AM",
    emailCount: 4,
  },
  {
    id: "12",
    client: "Street Wear Brands",
    invoices: "1 invoice\nFW-2024-2230",
    totalAmount: 4500,
    invoiceDate: "2025-06-25",     lastContact: "Initial payment request sent\nJul 24, 2025 12:30 AM",
    emailCount: 1,
  },
  {
    id: "13",
    client: "Designer Outlet Mall",
    invoices: "2 invoices\nFW-2024-2235, FW-2024-2236",
    totalAmount: 19600,
    invoiceDate: "2025-05-15",     lastContact: "Follow-up after phone call\nJul 18, 2025 12:30 AM",
    emailCount: 3,
  },
  {
    id: "14",
    client: "Boutique Collection Ltd",
    invoices: "1 invoice\nFW-2024-2240",
    totalAmount: 11200,
    invoiceDate: "2025-04-20",     lastContact: "Final demand letter sent\nJul 17, 2025 12:30 AM",
    emailCount: 2,
  },
  {
    id: "15",
    client: "Fashion Hub Central",
    invoices: "1 invoice\nFW-2024-2245",
    totalAmount: 6300,
    invoiceDate: "2025-07-20",     lastContact: "Account became overdue\nJul 26, 2025 12:30 AM",
    emailCount: 0,
  },
  {
    id: "16",
    client: "Elite Garments Inc",
    invoices: "1 invoice\nFW-2024-2250",
    totalAmount: 13400,
    invoiceDate: "2025-06-25",     lastContact: "Payment reminder initiated\nJul 21, 2025 12:30 AM",
    emailCount: 1,
  },
  {
    id: "17",
    client: "Trend Setters LLC",
    invoices: "2 invoices\nFW-2024-2255, FW-2024-2256",
    totalAmount: 18700,
    invoiceDate: "2025-05-15",     lastContact: "Phone call follow-up scheduled\nJul 16, 2025 12:30 AM",
    emailCount: 2,
  },
  {
    id: "18",
    client: "Casual Wear Collective",
    invoices: "1 invoice\nFW-2024-2260",
    totalAmount: 9100,
    invoiceDate: "2025-06-25",     lastContact: "Initial contact established\nJul 23, 2025 12:30 AM",
    emailCount: 1,
  },
  {
    id: "19",
    client: "Premium Fashion Group",
    invoices: "1 invoice\nFW-2024-2265",
    totalAmount: 22800,
    invoiceDate: "2024-02-15", // 160+ days overdue
    lastContact: "Account escalated to legal\nJul 15, 2025 12:30 AM",
    emailCount: 5,
  },
  {
    id: "20",
    client: "Style Maven Enterprises",
    invoices: "1 invoice\nFW-2024-2270",
    totalAmount: 5700,
    invoiceDate: "2025-04-20",     lastContact: "Final notice before collection\nJul 14, 2025 12:30 AM",
    emailCount: 3,
  },
  {
    id: "21",
    client: "Fashion Forward Retail",
    invoices: "1 invoice\nFW-2024-2275",
    totalAmount: 8200,
    invoiceDate: "2025-05-15",     lastContact: "Second follow-up completed\nJul 19, 2025 12:30 AM",
    emailCount: 2,
  },
  {
    id: "22",
    client: "Apparel Innovations Ltd",
    invoices: "1 invoice\nFW-2024-2280",
    totalAmount: 12900,
    invoiceDate: "2025-06-25",     lastContact: "Payment terms discussed\nJul 22, 2025 12:30 AM",
    emailCount: 1,
  },
  {
    id: "23",
    client: "Textile Solutions Corp",
    invoices: "2 invoices\nFW-2024-2285, FW-2024-2286",
    totalAmount: 15600,
    invoiceDate: "2025-07-20",     lastContact: "Recently became overdue\nJul 25, 2025 12:30 AM",
    emailCount: 0,
  },
  {
    id: "24",
    client: "Designer Collective LLC",
    invoices: "1 invoice\nFW-2024-2290",
    totalAmount: 7400,
    invoiceDate: "2025-05-15",     lastContact: "Awaiting payment confirmation\nJul 18, 2025 12:30 AM",
    emailCount: 2,
  },
];

function getEmailStageStyle(stage: string) {
  switch (stage) {
    case "Escalated":
      return { backgroundColor: "#FFD5D5", color: "#FF7676" };
    case "First Contact":
      return { backgroundColor: "#FFDBF5", color: "#DB97C8" };
    case "Friendly":
      return { backgroundColor: "#29DFB6", color: "#FFFFFF" };
    case "Urgent":
      return { backgroundColor: "#DB97C8", color: "#FFFFFF" };
    case "Final Notice":
      return { backgroundColor: "#FFEEB2", color: "#D97706" };
    default:
      return { backgroundColor: "#F3F4F6", color: "#6B7280" };
  }
}

// Pagination Component
function PaginationControls({ 
  currentPage, 
  totalPages, 
  itemsPerPage, 
  totalItems,
  onPageChange, 
  onItemsPerPageChange 
}: {
  currentPage: number;
  totalPages: number;
  itemsPerPage: number;
  totalItems: number;
  onPageChange: (page: number) => void;
  onItemsPerPageChange: (items: number) => void;
}) {
  const startItem = (currentPage - 1) * itemsPerPage + 1;
  const endItem = Math.min(currentPage * itemsPerPage, totalItems);

  const getPageNumbers = () => {
    const pages = [];
    const showPages = 5; // Show 5 page numbers max
    
    if (totalPages <= showPages) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      let start = Math.max(1, currentPage - 2);
      let end = Math.min(totalPages, start + showPages - 1);
      
      if (end - start < showPages - 1) {
        start = Math.max(1, end - showPages + 1);
      }
      
      for (let i = start; i <= end; i++) {
        pages.push(i);
      }
    }
    
    return pages;
  };

  return (
    <div className="flex items-center justify-between px-6 py-4 border-t border-gray-200 bg-white">
      <div className="flex items-center space-x-4">
        <div className="text-sm text-gray-600" style={{ fontFamily: "Poppins, system-ui, sans-serif" }}>
          Showing {startItem}-{endItem} of {totalItems} entries
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-600" style={{ fontFamily: "Poppins, system-ui, sans-serif" }}>
            Show:
          </span>
          <select
            value={itemsPerPage}
            onChange={(e) => onItemsPerPageChange(Number(e.target.value))}
            className="border border-gray-300 rounded px-3 py-1 text-sm focus:outline-none focus:border-blue-500"
            style={{ fontFamily: "Poppins, system-ui, sans-serif" }}
          >
            <option value={10}>10</option>
            <option value={25}>25</option>
            <option value={50}>50</option>
          </select>
        </div>
      </div>
      
      <div className="flex items-center space-x-2">
        <button
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage === 1}
          className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          style={{ fontFamily: "Poppins, system-ui, sans-serif" }}
        >
          Previous
        </button>
        
        {getPageNumbers().map((page) => (
          <button
            key={page}
            onClick={() => onPageChange(page)}
            className={`px-3 py-1 text-sm border rounded ${
              page === currentPage
                ? "bg-blue-500 text-white border-blue-500"
                : "border-gray-300 hover:bg-gray-50"
            }`}
            style={{ fontFamily: "Poppins, system-ui, sans-serif" }}
          >
            {page}
          </button>
        ))}
        
        <button
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
          className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          style={{ fontFamily: "Poppins, system-ui, sans-serif" }}
        >
          Next
        </button>
      </div>
    </div>
  );
}

export default function ActiveCollectionsPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedItems, setSelectedItems] = useState<Set<string>>(new Set());
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(10);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedWorkflow, setSelectedWorkflow] = useState<EmailCollectionWorkflow | null>(null);

  // Initialize page from URL
  useEffect(() => {
    const pageParam = searchParams.get('page');
    if (pageParam) {
      setCurrentPage(Number(pageParam));
    }
  }, [searchParams]);

  // Update URL when page changes
  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    const params = new URLSearchParams(searchParams.toString());
    params.set('page', page.toString());
    router.push(`/active-collections?${params.toString()}`);
  };

  const handleItemsPerPageChange = (items: number) => {
    setItemsPerPage(items);
    setCurrentPage(1); // Reset to first page when changing items per page
    const params = new URLSearchParams(searchParams.toString());
    params.set('page', '1');
    router.push(`/active-collections?${params.toString()}`);
  };

  // Filter and paginate data
  const filteredData = mockActiveCollections.filter(item =>
    item.client.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.invoices.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const totalPages = Math.ceil(filteredData.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const paginatedData = filteredData.slice(startIndex, startIndex + itemsPerPage);

  // Reset to page 1 when search changes
  useEffect(() => {
    setCurrentPage(1);
    const params = new URLSearchParams(searchParams.toString());
    params.set('page', '1');
    router.push(`/active-collections?${params.toString()}`);
  }, [searchTerm]);

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedItems(new Set(paginatedData.map(item => item.id)));
    } else {
      setSelectedItems(new Set());
    }
  };

  const handleSelectItem = (id: string, checked: boolean) => {
    const newSelected = new Set(selectedItems);
    if (checked) {
      newSelected.add(id);
    } else {
      newSelected.delete(id);
    }
    setSelectedItems(newSelected);
  };

  const handleOpenWorkflow = (item: any) => {
    const daysOverdue = calculateDaysOverdue(item.invoiceDate);
    const currentStage = getEmailStageFromDays(daysOverdue);
    
    // Create workflow stages based on current progress
    const stages = [
      {
        id: "1",
        name: "Initial Contact",
        day: 1,
        status: (daysOverdue > 0 ? 'completed' : 'current') as 'completed' | 'current' | 'pending',
        description: "Send first payment reminder email with invoice details and payment options.",
        actions: [
          "Send payment reminder",
          "Include payment portal link",
          "Set follow-up reminder"
        ]
      },
      {
        id: "2", 
        name: "Follow-up",
        day: 7,
        status: (daysOverdue > 30 ? 'completed' : daysOverdue > 0 ? 'current' : 'pending') as 'completed' | 'current' | 'pending',
        description: "Follow up with second payment reminder if no response received.",
        actions: [
          "Send follow-up reminder",
          "Update payment terms",
          "Schedule phone call"
        ]
      },
      {
        id: "3",
        name: "Final Notice", 
        day: 14,
        status: (daysOverdue > 60 ? 'completed' : daysOverdue > 30 ? 'current' : 'pending') as 'completed' | 'current' | 'pending',
        description: "Send final notice before escalation with clear next steps.",
        actions: [
          "Send final notice",
          "Set escalation date",
          "Prepare collection process"
        ]
      },
      {
        id: "4",
        name: "Escalation",
        day: 21,
        status: (daysOverdue > 90 ? 'completed' : daysOverdue > 60 ? 'current' : 'pending') as 'completed' | 'current' | 'pending',
        description: "Escalate to collection agency or legal action.",
        actions: [
          "Transfer to collections",
          "Legal notice preparation",
          "Account review"
        ]
      },
      {
        id: "5",
        name: "Resolution",
        day: 30,
        status: (daysOverdue > 120 ? 'current' : 'pending') as 'completed' | 'current' | 'pending',
        description: "Final resolution - payment received or account written off.",
        actions: [
          "Process payment",
          "Close account",
          "Update records"
        ]
      }
    ];

    const workflowData: EmailCollectionWorkflow = {
      clientName: item.client,
      totalAmount: item.totalAmount,
      invoiceCount: parseInt(item.invoices.split(' ')[0]),
      stages,
      lastContact: item.lastContact.split('\n')[1] || item.lastContact,
      totalEmails: item.emailCount,
      currentStage: currentStage
    };

    setSelectedWorkflow(workflowData);
    setIsModalOpen(true);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      
      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 
              className="text-2xl font-semibold text-black"
              style={{ fontFamily: "Poppins, system-ui, sans-serif" }}
            >
              Active Collections
            </h1>
            <p 
              className="text-sm text-gray-600"
              style={{ fontFamily: "Poppins, system-ui, sans-serif" }}
            >
              Email-based collections workflow - grouped by client
            </p>
          </div>
          <div className="text-sm text-gray-500" style={{ fontFamily: "Poppins, system-ui, sans-serif" }}>
            {filteredData.length} of {mockActiveCollections.length} clients
          </div>
        </div>

        {/* Search Bar - Fully Rounded */}
        <div className="mb-6">
          <div className="relative">
            <input
              type="text"
              placeholder="Search clients, invoices, or communications..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full h-12 pl-10 pr-4 rounded-full border border-gray-200 bg-white focus:outline-none focus:border-blue-500 transition-colors"
              style={{ fontFamily: "Poppins, system-ui, sans-serif" }}
            />
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              fill="none" 
              viewBox="0 0 24 24" 
              strokeWidth="1.5" 
              stroke="currentColor" 
              className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" 
              />
            </svg>
          </div>
        </div>

        <div className="rounded-lg border border-gray-200 overflow-hidden" style={{ backgroundColor: "#F8F5F4" }}>
          <table className="w-full">
            <thead style={{ backgroundColor: "#1E84FF" }} className="border-b border-gray-200">
              <tr>
                <th className="w-12 px-6 py-4 text-left">
                  <input
                    type="checkbox"
                    checked={selectedItems.size === paginatedData.length && paginatedData.length > 0}
                    onChange={(e) => handleSelectAll(e.target.checked)}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                </th>
                <th className="px-6 py-4 text-left text-sm font-bold text-white uppercase tracking-wider" style={{ fontFamily: "Poppins, system-ui, sans-serif" }}>
                  CLIENT
                </th>
                <th className="px-6 py-4 text-left text-sm font-bold text-white uppercase tracking-wider" style={{ fontFamily: "Poppins, system-ui, sans-serif" }}>
                  INVOICES
                </th>
                <th className="px-6 py-4 text-left text-sm font-bold text-white uppercase tracking-wider" style={{ fontFamily: "Poppins, system-ui, sans-serif" }}>
                  TOTAL AMOUNT
                </th>
                <th className="px-6 py-4 text-left text-sm font-bold text-white uppercase tracking-wider" style={{ fontFamily: "Poppins, system-ui, sans-serif" }}>
                  EMAIL STAGE
                </th>
                <th className="px-6 py-4 text-left text-sm font-bold text-white uppercase tracking-wider" style={{ fontFamily: "Poppins, system-ui, sans-serif" }}>
                  LAST CONTACT
                </th>
                <th className="px-6 py-4 text-left text-sm font-bold text-white uppercase tracking-wider" style={{ fontFamily: "Poppins, system-ui, sans-serif" }}>
                  EMAILS
                </th>
                <th className="px-6 py-4 text-left text-sm font-bold text-white uppercase tracking-wider" style={{ fontFamily: "Poppins, system-ui, sans-serif" }}>
                  ACTIONS
                </th>
              </tr>
            </thead>
            <tbody className="bg-transparent">
              {paginatedData.map((item, index) => (
                <tr key={item.id} className={index % 2 === 0 ? "bg-transparent" : "bg-white bg-opacity-30"}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <input
                      type="checkbox"
                      checked={selectedItems.has(item.id)}
                      onChange={(e) => handleSelectItem(item.id, e.target.checked)}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="font-medium text-black" style={{ fontFamily: "Poppins, system-ui, sans-serif" }}>
                      {item.client}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-600" style={{ fontFamily: "Poppins, system-ui, sans-serif" }}>
                      {item.invoices.split('\n').map((line, i) => (
                        <div key={i}>{line}</div>
                      ))}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="font-semibold text-black" style={{ fontFamily: "Poppins, system-ui, sans-serif" }}>
                      ${item.totalAmount.toLocaleString()}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {(() => {
                      const daysOverdue = calculateDaysOverdue(item.invoiceDate);
                      const emailStage = getEmailStageFromDays(daysOverdue);
                      return (
                        <span 
                          className="inline-flex px-3 py-1 rounded-full text-xs font-medium"
                          style={{ 
                            fontFamily: "Poppins, system-ui, sans-serif",
                            ...getEmailStageStyle(emailStage)
                          }}
                        >
                          {emailStage}
                        </span>
                      );
                    })()}
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-600" style={{ fontFamily: "Poppins, system-ui, sans-serif" }}>
                      {item.lastContact.split('\n').map((line, i) => (
                        <div key={i} className={i === 1 ? "text-gray-400" : ""}>{line}</div>
                      ))}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center space-x-2">
                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="w-4 h-4 text-gray-400">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 0 1-2.25 2.25h-15a2.25 2.25 0 0 1-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0 0 19.5 4.5h-15a2.25 2.25 0 0 0-2.25 2.25m19.5 0v.243a2.25 2.25 0 0 1-1.07 1.916l-7.5 4.615a2.25 2.25 0 0 1-2.36 0L3.32 8.91a2.25 2.25 0 0 1-1.07-1.916V6.75" />
                      </svg>
                      <span className="text-sm text-gray-600" style={{ fontFamily: "Poppins, system-ui, sans-serif" }}>
                        {item.emailCount}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <button 
                      onClick={() => handleOpenWorkflow(item)}
                      className="text-gray-400 hover:text-gray-600 transition-colors"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="w-5 h-5">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" />
                        <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
                      </svg>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          
          {/* Pagination Controls */}
          <PaginationControls
            currentPage={currentPage}
            totalPages={totalPages}
            itemsPerPage={itemsPerPage}
            totalItems={filteredData.length}
            onPageChange={handlePageChange}
            onItemsPerPageChange={handleItemsPerPageChange}
          />
        </div>

        {/* Email Workflow Modal */}
        {selectedWorkflow && (
          <EmailWorkflowModal
            isOpen={isModalOpen}
            onClose={() => {
              setIsModalOpen(false);
              setSelectedWorkflow(null);
            }}
            workflowData={selectedWorkflow}
          />
        )}
      </main>
    </div>
  );
}