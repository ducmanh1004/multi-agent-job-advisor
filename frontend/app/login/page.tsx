"use client";

import { useState } from "react";
import { LogIn, UserPlus } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Panel, PanelTitle } from "@/components/ui/panel";
import { supabase } from "@/lib/supabase";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState(supabase ? "" : "Local mode: Supabase environment variables are not configured.");

  async function signIn() {
    if (!supabase) return;
    const { error } = await supabase.auth.signInWithPassword({ email, password });
    setMessage(error ? error.message : "Signed in.");
  }

  async function signUp() {
    if (!supabase) return;
    const { error } = await supabase.auth.signUp({ email, password });
    setMessage(error ? error.message : "Registration submitted.");
  }

  return (
    <div className="mx-auto max-w-xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Login</h1>
        <p className="mt-1 text-sm text-muted">Supabase Auth email and password.</p>
      </div>
      <Panel>
        <PanelTitle title="Account" />
        <div className="space-y-4">
          <Input type="email" placeholder="Email" value={email} onChange={(event) => setEmail(event.target.value)} />
          <Input type="password" placeholder="Password" value={password} onChange={(event) => setPassword(event.target.value)} />
          <div className="flex gap-2">
            <Button onClick={signIn} disabled={!supabase}>
              <LogIn size={16} />
              Sign In
            </Button>
            <Button onClick={signUp} variant="secondary" disabled={!supabase}>
              <UserPlus size={16} />
              Register
            </Button>
          </div>
          {message ? <div className="rounded-md border border-border bg-slate-50 p-3 text-sm text-muted">{message}</div> : null}
        </div>
      </Panel>
    </div>
  );
}

