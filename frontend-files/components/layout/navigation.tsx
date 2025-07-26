"use client";

import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface NavigationButtonProps {
  href: string;
  icon: string;
  label: string;
  active: boolean;
}

function NavigationButton({
  href,
  icon,
  label,
  active,
}: NavigationButtonProps) {
  return (
    <Link href={href}>
      <Button
        variant="ghost"
        className={cn(
          "h-11 px-4 py-2 rounded-full border transition-all duration-200",
          "text-sm text-black space-x-2",
          active
            ? "border-gray-200 bg-white font-semibold"
            : "bg-transparent border-gray-200 hover:bg-gray-50 font-medium"
        )}
        style={{ 
          fontFamily: "Poppins, system-ui, sans-serif"
        }}
      >
        <Image
          src={icon}
          alt={`${label} icon`}
          width={16}
          height={16}
          className="w-4 h-4"
          style={{
            filter: active ? 'none' : 'grayscale(100%) brightness(0.6)'
          }}
        />
        <span>{label}</span>
      </Button>
    </Link>
  );
}

export function Navigation() {
  const pathname = usePathname();

  return (
    <nav
      className="w-full py-4"
      style={{
        backgroundColor: "#FCFCFC",
      }}
    >
      <div className="max-w-7xl mx-auto px-6 flex items-center justify-between">
        <div className="flex items-center space-x-8">
          <Link href="/">
            <Image
              src="/noodle-seed-logo.svg"
              alt="Noodle Seed Logo"
              width={340}
              height={44}
              className="h-11 w-auto"
            />
          </Link>
          
          <div className="flex items-center space-x-4">
            <NavigationButton
              href="/"
              icon="/home-icon.svg"
              label="Home"
              active={pathname === "/"}
            />
            <NavigationButton
              href="/active-collections"
              icon="/active-collections-icon.svg"
              label="Active Collections"
              active={pathname === "/active-collections"}
            />
          </div>
        </div>

        <div className="flex items-center space-x-4">
          {/* Search Bar */}
          <div className="relative">
            <input
              type="text"
              placeholder="Search..."
              className="w-64 h-11 pl-10 pr-4 rounded-full border border-gray-200 bg-white focus:outline-none focus:border-blue-500 transition-colors"
              style={{ fontFamily: 'Poppins, system-ui, sans-serif' }}
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
          
          {/* Settings Button */}
          <Button
            variant="ghost"
            size="icon"
            className="w-11 h-11 hover:bg-gray-100 rounded-full"
            title="Settings page"
          >
            <svg 
              width="64" 
              height="64" 
              viewBox="0 0 64 64" 
              fill="none" 
              xmlns="http://www.w3.org/2000/svg"
              className="w-8 h-8"
            >
              <path 
                d="M29.3041 11.1633C29.5591 9.62767 30.8908 8.5 32.4491 8.5H35.5459C37.1043 8.5 38.4359 9.62767 38.6909 11.1633L39.1131 13.6963C39.3114 14.8977 40.2011 15.861 41.3231 16.3313C42.4508 16.796 43.7456 16.7337 44.7373 16.0253L46.8254 14.5322C47.4396 14.0932 48.1896 13.8864 48.942 13.9486C49.6943 14.0109 50.4001 14.3382 50.9338 14.8722L53.1239 17.0652C54.2289 18.1673 54.3706 19.9042 53.4639 21.1735L51.9708 23.2617C51.2624 24.2533 51.2001 25.5453 51.6676 26.673C52.1351 27.7978 53.0984 28.6847 54.3026 28.883L56.8328 29.308C58.3713 29.563 59.4961 30.8918 59.4961 32.4502V35.5498C59.4961 37.1082 58.3713 38.4398 56.8328 38.6948L54.2998 39.117C53.0984 39.3153 52.1351 40.2022 51.6676 41.327C51.2001 42.4547 51.2624 43.7467 51.9708 44.7383L53.4639 46.8293C54.3706 48.0958 54.2261 49.8327 53.1239 50.9377L50.9309 53.1278C50.3975 53.6611 49.6922 53.9879 48.9405 54.0502C48.1888 54.1124 47.4393 53.9061 46.8254 53.4678L44.7344 51.9747C43.7428 51.2663 42.4508 51.204 41.3259 51.6715C40.1983 52.139 39.3143 53.1023 39.1131 54.3037L38.6909 56.8367C38.4359 58.3723 37.1043 59.5 35.5459 59.5H32.4463C30.8879 59.5 29.5591 58.3723 29.3013 56.8367L28.8819 54.3037C28.6808 53.1023 27.7939 52.139 26.6691 51.6687C25.5414 51.204 24.2494 51.2663 23.2578 51.9747L21.1668 53.4678C19.9003 54.3745 18.1634 54.23 17.0584 53.1278L14.8683 50.9348C14.3343 50.4012 14.007 49.6954 13.9447 48.943C13.8825 48.1907 14.0892 47.4406 14.5283 46.8265L16.0214 44.7383C16.7298 43.7467 16.7921 42.4547 16.3274 41.327C15.8599 40.2022 14.8938 39.3153 13.6924 39.117L11.1594 38.692C9.62376 38.437 8.49609 37.1053 8.49609 35.5498V32.4502C8.49609 30.8918 9.62376 29.5602 11.1594 29.3052L13.6924 28.883C14.8938 28.6847 15.8599 27.7978 16.3274 26.673C16.7949 25.5453 16.7326 24.2533 16.0214 23.2617L14.5311 21.1707C14.0921 20.5565 13.8853 19.8065 13.9476 19.0541C14.0098 18.3018 14.3371 17.596 14.8711 17.0623L17.0613 14.8722C17.5949 14.3382 18.3007 14.0109 19.0531 13.9486C19.8054 13.8864 20.5554 14.0932 21.1696 14.5322L23.2578 16.0253C24.2494 16.7337 25.5443 16.796 26.6691 16.3285C27.7939 15.861 28.6808 14.8977 28.8791 13.6963L29.3041 11.1633Z" 
                stroke="currentColor" 
                strokeWidth="3" 
                strokeLinecap="round" 
                strokeLinejoin="round"
              />
              <path 
                d="M42.5 34C42.5 36.2543 41.6045 38.4163 40.0104 40.0104C38.4163 41.6045 36.2543 42.5 34 42.5C31.7457 42.5 29.5837 41.6045 27.9896 40.0104C26.3955 38.4163 25.5 36.2543 25.5 34C25.5 31.7457 26.3955 29.5837 27.9896 27.9896C29.5837 26.3955 31.7457 25.5 34 25.5C36.2543 25.5 38.4163 26.3955 40.0104 27.9896C41.6045 29.5837 42.5 31.7457 42.5 34Z" 
                stroke="currentColor" 
                strokeWidth="3" 
                strokeLinecap="round" 
                strokeLinejoin="round"
              />
            </svg>
          </Button>
        </div>
      </div>
    </nav>
  );
}
