import { Bell, CreditCard, KeyRound, Lock, User } from "lucide-react";
import { PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";

export default function SettingsPage() {
  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Settings"
        title="Workspace and security settings."
        description="Manage profile details, privacy defaults, usage limits, and API security controls."
      />

      <div className="grid gap-6 lg:grid-cols-[1fr_360px]">
        <section className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><User className="h-5 w-5 text-primary" /> Profile</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-5 sm:grid-cols-2">
              <div className="space-y-2">
                <Label>Full name</Label>
                <Input defaultValue="Subhash Builder" />
              </div>
              <div className="space-y-2">
                <Label>Email</Label>
                <Input defaultValue="demo@custommodel.ai" />
              </div>
              <div className="space-y-2 sm:col-span-2">
                <Label>Workspace name</Label>
                <Input defaultValue="CustomModel Lab" />
              </div>
              <div className="sm:col-span-2">
                <Button>Save profile</Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><Lock className="h-5 w-5 text-primary" /> Privacy defaults</CardTitle>
            </CardHeader>
            <CardContent className="space-y-5">
              <div className="space-y-2">
                <Label>Default model visibility</Label>
                <Select defaultValue="Private">
                  <option>Private</option>
                  <option>Workspace</option>
                  <option>Public</option>
                </Select>
              </div>
              <div className="rounded-2xl bg-muted p-4 text-sm leading-6 text-muted-foreground">
                Recommended: keep new models private until the owner explicitly deploys or shares them.
              </div>
            </CardContent>
          </Card>
        </section>

        <aside className="space-y-6">
          {[
            { icon: KeyRound, title: "API security", text: "Rotate keys regularly and store only key hashes in the backend." },
            { icon: CreditCard, title: "Usage limits", text: "Mock plan: 50k API requests per month and 10 training jobs." },
            { icon: Bell, title: "Notifications", text: "Training completion and failed job alerts will appear here." }
          ].map((item) => {
            const Icon = item.icon;
            return (
              <Card key={item.title}>
                <CardContent className="p-6">
                  <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-secondary text-secondary-foreground">
                    <Icon className="h-5 w-5" />
                  </div>
                  <h3 className="font-semibold">{item.title}</h3>
                  <p className="mt-2 text-sm leading-6 text-muted-foreground">{item.text}</p>
                </CardContent>
              </Card>
            );
          })}
        </aside>
      </div>
    </div>
  );
}
