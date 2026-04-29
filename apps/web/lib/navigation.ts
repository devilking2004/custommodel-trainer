import {
  Activity,
  BarChart3,
  Blocks,
  Bot,
  Braces,
  Gauge,
  History,
  Home,
  KeyRound,
  MessageSquareHeart,
  PlayCircle,
  Settings,
  SlidersHorizontal,
  UploadCloud
} from "lucide-react";
import { demoModelId } from "@/lib/mock-data";

export const appNavigation = [
  { label: "Dashboard", href: "/dashboard", icon: Home },
  { label: "Create Model", href: "/models/new", icon: Blocks },
  { label: "Model Setup", href: `/models/${demoModelId}/setup`, icon: SlidersHorizontal },
  { label: "Data Upload", href: `/models/${demoModelId}/data`, icon: UploadCloud },
  { label: "Readiness Score", href: `/models/${demoModelId}/readiness`, icon: Gauge },
  { label: "Training", href: `/models/${demoModelId}/training`, icon: Activity },
  { label: "Playground", href: `/models/${demoModelId}/playground`, icon: PlayCircle },
  { label: "API Usage", href: `/models/${demoModelId}/api`, icon: Braces },
  { label: "Feedback", href: `/models/${demoModelId}/feedback`, icon: MessageSquareHeart },
  { label: "Versions", href: `/models/${demoModelId}/versions`, icon: History },
  { label: "Settings", href: "/settings", icon: Settings }
];

export const quickStats = [
  { label: "Active models", value: "3", icon: Bot, helper: "+1 this month" },
  { label: "API requests", value: "29.9k", icon: BarChart3, helper: "Last 7 days" },
  { label: "API keys", value: "4", icon: KeyRound, helper: "2 production" }
];
