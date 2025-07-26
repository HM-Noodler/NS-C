import Image from "next/image";
import { Button } from "@/components/ui/button";

export function FileUpload() {
  return (
    <div className="mb-8">
      <div className="flex items-center space-x-4 mb-6">
        <Image
          src="/fineman-concierge.svg"
          alt="Fineman Concierge icon"
          width={80}
          height={80}
          className="w-20 h-20"
        />
        <h2
          className="font-semibold text-black"
          style={{
            fontFamily: "Poppins, system-ui, sans-serif",
            fontSize: "36px",
            lineHeight: "1.2",
          }}
        >
          Your Concierge Status
        </h2>
      </div>

      <div className="flex items-center justify-between mb-6">
        <Button
          variant="outline"
          className="h-8 px-4 text-sm font-medium text-white border-0 hover:text-white"
          style={{
            fontFamily: "Poppins, system-ui, sans-serif",
            borderRadius: "0px 8px 0px 8px",
            backgroundColor: "#1E84FF",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = "#1976D2";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = "#1E84FF";
          }}
        >
          Upload File
          <Image
            src="/upload-file-icon.svg"
            alt="Upload file icon"
            width={16}
            height={16}
            className="w-4 h-4 ml-2"
            style={{
              filter:
                "brightness(0) saturate(100%) invert(100%) sepia(0%) saturate(0%) hue-rotate(0deg) brightness(100%) contrast(100%)",
            }}
          />
        </Button>
      </div>
    </div>
  );
}