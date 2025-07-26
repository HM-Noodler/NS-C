"use client";

import { useState } from "react";
import { EmailCollectionWorkflow } from "@/types";
import { WorkflowProgressFlow } from "./workflow-progress-flow";

interface EmailWorkflowModalProps {
  isOpen: boolean;
  onClose: () => void;
  workflowData: EmailCollectionWorkflow;
}

export function EmailWorkflowModal({ isOpen, onClose, workflowData }: EmailWorkflowModalProps) {
  const [activeTab, setActiveTab] = useState("workflow-overview");

  if (!isOpen) return null;

  const tabs = [
    { id: "workflow-overview", label: "Workflow Overview" },
    { id: "email-history", label: `Email History (${workflowData.totalEmails})` },
    { id: "manual-response", label: "Manual Response" }
  ];

  const currentStageData = workflowData.stages.find(stage => stage.status === 'current');

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="relative bg-white rounded-lg shadow-xl w-full max-w-6xl max-h-[90vh] overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
            <div>
              <h2 
                className="text-xl font-semibold text-black"
                style={{ fontFamily: "Poppins, system-ui, sans-serif" }}
              >
                Email Collection Workflow
              </h2>
              <p 
                className="text-sm text-gray-600 mt-1"
                style={{ fontFamily: "Poppins, system-ui, sans-serif" }}
              >
                {workflowData.clientName} • ${workflowData.totalAmount.toLocaleString()} • {workflowData.invoiceCount} invoices
              </p>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Tab Navigation */}
          <div className="border-b border-gray-200">
            <nav className="flex px-6">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-3 px-4 text-sm font-medium border-b-2 transition-colors ${
                    activeTab === tab.id
                      ? "text-blue-600 border-blue-600"
                      : "text-gray-500 border-transparent hover:text-gray-700 hover:border-gray-300"
                  }`}
                  style={{ fontFamily: "Poppins, system-ui, sans-serif" }}
                >
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>

          {/* Modal Content */}
          <div className="overflow-y-auto max-h-[calc(90vh-180px)]">
            {activeTab === "workflow-overview" && (
              <div className="p-6">
                {/* Workflow Progress */}
                <WorkflowProgressFlow 
                  stages={workflowData.stages} 
                  currentStage={workflowData.currentStage} 
                />

                {/* Current Stage Details */}
                {currentStageData && (
                  <div className="bg-gray-50 rounded-lg p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center">
                          <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        </div>
                        <h3 
                          className="text-lg font-semibold text-black"
                          style={{ fontFamily: "Poppins, system-ui, sans-serif" }}
                        >
                          {currentStageData.name}
                        </h3>
                      </div>
                      <span 
                        className="text-sm text-green-600 bg-green-100 px-3 py-1 rounded-full"
                        style={{ fontFamily: "Poppins, system-ui, sans-serif" }}
                      >
                        Day {currentStageData.day}
                      </span>
                    </div>

                    <p 
                      className="text-gray-600 mb-4"
                      style={{ fontFamily: "Poppins, system-ui, sans-serif" }}
                    >
                      {currentStageData.description}
                    </p>

                    <div>
                      <h4 
                        className="text-sm font-medium text-gray-900 mb-3"
                        style={{ fontFamily: "Poppins, system-ui, sans-serif" }}
                      >
                        Key Actions:
                      </h4>
                      <ul className="space-y-2">
                        {currentStageData.actions.map((action, index) => (
                          <li key={index} className="flex items-center space-x-3">
                            <div className="w-2 h-2 bg-blue-500 rounded-full flex-shrink-0" />
                            <span 
                              className="text-sm text-gray-600"
                              style={{ fontFamily: "Poppins, system-ui, sans-serif" }}
                            >
                              {action}
                            </span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}

                {/* Action Footer */}
                <div className="flex items-center justify-between mt-6 pt-6 border-t border-gray-200">
                  <div className="text-sm text-gray-600" style={{ fontFamily: "Poppins, system-ui, sans-serif" }}>
                    Last Contact: {workflowData.lastContact} • {workflowData.totalEmails} total emails
                  </div>
                  <div className="flex space-x-3">
                    <button className="flex items-center space-x-2 px-4 py-2 text-red-600 bg-red-50 border border-red-200 rounded-lg hover:bg-red-100 transition-colors">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728L5.636 5.636m12.728 12.728L18.364 5.636M5.636 18.364l12.728-12.728" />
                      </svg>
                      <span className="text-sm font-medium" style={{ fontFamily: "Poppins, system-ui, sans-serif" }}>
                        Add to DNC
                      </span>
                    </button>
                    <button className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                      <span className="text-sm font-medium" style={{ fontFamily: "Poppins, system-ui, sans-serif" }}>
                        Close
                      </span>
                    </button>
                  </div>
                </div>
              </div>
            )}

            {activeTab === "email-history" && (
              <div className="p-6">
                <div className="text-center py-12">
                  <div className="w-16 h-16 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
                    <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2" style={{ fontFamily: "Poppins, system-ui, sans-serif" }}>
                    Email History
                  </h3>
                  <p className="text-gray-600" style={{ fontFamily: "Poppins, system-ui, sans-serif" }}>
                    Email communication history will be displayed here
                  </p>
                </div>
              </div>
            )}

            {activeTab === "manual-response" && (
              <div className="p-6">
                <div className="text-center py-12">
                  <div className="w-16 h-16 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
                    <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2" style={{ fontFamily: "Poppins, system-ui, sans-serif" }}>
                    Manual Response
                  </h3>
                  <p className="text-gray-600" style={{ fontFamily: "Poppins, system-ui, sans-serif" }}>
                    Manual email composition and response tools will be available here
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}