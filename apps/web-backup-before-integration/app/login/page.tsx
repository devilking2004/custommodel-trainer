"use client";

import Link from "next/link";
import { useState } from "react";
import { ArrowRight } from "lucide-react";
import { AuthShell } from "@/components/layout/auth-shell";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function LoginPage() {
  const [loading, setLoading] = useState(false);

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    window.setTimeout(() => {
      window.location.href = "/dashboard";
    }, 500);
  }

  return (
    <AuthShell title="Welcome back" subtitle="Login with mock credentials and continue to your dashboard.">
      <form className="space-y-5" onSubmit={handleSubmit}>
        <div className="space-y-2">
          <Label htmlFor="email">Email</Label>
          <Input id="email" type="email" defaultValue="demo@custommodel.ai" required />
        </div>
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <Label htmlFor="password">Password</Label>
            <Link href="#" className="text-sm font-medium text-primary hover:underline">Forgot password?</Link>
          </div>
          <Input id="password" type="password" defaultValue="Password123!" required />
        </div>
        <Button className="w-full" type="submit" disabled={loading}>
          {loading ? "Opening dashboard..." : "Login"}
          <ArrowRight className="h-4 w-4" />
        </Button>
      </form>
      <p className="mt-6 text-center text-sm text-muted-foreground">
        New to CustomModel Trainer?{' '}
        <Link href="/signup" className="font-semibold text-primary hover:underline">Create an account</Link>
      </p>
    </AuthShell>
  );
}
