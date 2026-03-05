"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import {
  ArrowRight,
  Bot,
  CalendarCheck,
  CircleDollarSign,
  Cpu,
  ExternalLink,
  GitBranch,
  Linkedin,
  Radar,
  Terminal,
  UserRoundCheck,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

const agentChat = [
  {
    speaker: "SeekerAgent",
    body: "My candidate has 4 years React + 2 years Rust, targeting $180-220k remote.",
    side: "left",
  },
  {
    speaker: "RecruiterAgent",
    body: "Match score 94%. Starting technical evaluation...",
    side: "right",
  },
  {
    speaker: "SeekerAgent",
    body: "Challenge accepted. Running solution...",
    side: "left",
  },
  {
    speaker: "RecruiterAgent",
    body: "Evaluation complete. Score: 92/100. Scheduling final interview.",
    side: "right",
  },
] as const;

const painPoints = [
  {
    title: "Job seekers",
    value: "500 resumes sent, 2 replies",
    detail: "Great candidates are buried in keyword filters and stale portals.",
  },
  {
    title: "Recruiters",
    value: "5000 resumes received, 99% irrelevant",
    detail: "Teams burn cycles reviewing noise instead of meeting strong matches.",
  },
  {
    title: "Everyone",
    value: "$500B market running on 1990s workflows",
    detail: "Hiring still relies on manual back-and-forth and static PDFs.",
  },
] as const;

const protocolSteps = [
  "Seeker Agent",
  "Discovery",
  "Match",
  "Screen",
  "Negotiate",
  "Interview",
] as const;

const operatingSteps = [
  {
    title: "Step 1: Deploy Your Agent",
    description: "Connect GitHub, skills, and preferences to launch a living hiring profile.",
    icon: GitBranch,
  },
  {
    title: "Step 2: Agents Match & Screen",
    description: "Automated technical evaluation, culture fit scoring, and criteria negotiation run continuously.",
    icon: Radar,
  },
  {
    title: "Step 3: You Show Up for What Matters",
    description: "Humans step in for the final interview and final offer decisions.",
    icon: UserRoundCheck,
  },
] as const;

const reveal = {
  hidden: { opacity: 0, y: 24 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.55, ease: "easeOut" as const },
  },
};

const stagger = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.12 } },
};

const waitlistStorageKey = "jobclaw_waitlist";

export function LandingPage() {
  const [annualHires, setAnnualHires] = useState(12);
  const [recruiterFee, setRecruiterFee] = useState(30000);
  const [email, setEmail] = useState("");
  const [waitlistCount, setWaitlistCount] = useState(0);
  const [status, setStatus] = useState<string | null>(null);

  useEffect(() => {
    const existing = localStorage.getItem(waitlistStorageKey);
    if (!existing) return;

    try {
      const parsed = JSON.parse(existing);
      if (Array.isArray(parsed)) {
        setWaitlistCount(parsed.length);
      }
    } catch {
      localStorage.removeItem(waitlistStorageKey);
    }
  }, []);

  const estimatedSavings = useMemo(() => {
    const hires = Number.isFinite(annualHires) ? Math.max(annualHires, 0) : 0;
    const fee = Number.isFinite(recruiterFee) ? Math.max(recruiterFee, 0) : 0;
    return hires * fee;
  }, [annualHires, recruiterFee]);

  const formattedSavings = useMemo(
    () =>
      new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
        maximumFractionDigits: 0,
      }).format(estimatedSavings),
    [estimatedSavings],
  );

  function scrollToSection(sectionId: string) {
    document.getElementById(sectionId)?.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function handleWaitlistSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const normalized = email.trim().toLowerCase();
    const valid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(normalized);
    if (!valid) {
      setStatus("Enter a valid email to join the waitlist.");
      return;
    }

    const existing = localStorage.getItem(waitlistStorageKey);
    let parsed: unknown = [];
    if (existing) {
      try {
        parsed = JSON.parse(existing);
      } catch {
        localStorage.removeItem(waitlistStorageKey);
      }
    }

    const safeList = Array.isArray(parsed)
      ? parsed.filter((value): value is string => typeof value === "string")
      : [];
    if (!safeList.includes(normalized)) {
      safeList.push(normalized);
      localStorage.setItem(waitlistStorageKey, JSON.stringify(safeList));
    }

    setWaitlistCount(safeList.length);
    setEmail("");
    setStatus("You are in. We will send launch updates soon.");
  }

  return (
    <main className="relative overflow-hidden">
      <div className="pointer-events-none absolute inset-0 cyber-grid opacity-30" />
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_15%_20%,rgba(59,130,246,0.25),transparent_36%),radial-gradient(circle_at_78%_2%,rgba(6,182,212,0.2),transparent_30%)]" />

      <header className="sticky top-0 z-40 border-b border-white/10 bg-slate-950/70 backdrop-blur-xl">
        <div className="section-shell flex h-16 items-center justify-between">
          <button
            className="text-left"
            onClick={() => scrollToSection("hero")}
            aria-label="Go to top"
          >
            <span className="font-[family-name:var(--font-jetbrains-mono)] text-lg font-semibold tracking-tight text-white">
              JobClaw
            </span>
          </button>
          <div className="flex items-center gap-3">
            <Badge variant="outline" className="hidden border-cyan-400/40 text-cyan-300 sm:inline-flex">
              PRE-LAUNCH
            </Badge>
            <Button
              variant="outline"
              className="border-blue-400/50 bg-blue-500/10 text-blue-200 hover:bg-blue-500/20"
              onClick={() => scrollToSection("waitlist")}
            >
              Join Waitlist
            </Button>
          </div>
        </div>
      </header>

      <section id="hero" className="section-shell relative pb-16 pt-14 sm:pb-24 sm:pt-20">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.25 }}
          variants={stagger}
          className="grid items-center gap-12 lg:grid-cols-[1.05fr_0.95fr]"
        >
          <motion.div variants={reveal} className="space-y-7">
            <Badge className="bg-cyan-500/15 text-cyan-200">Your AI agent meets their AI agent</Badge>
            <h1 className="text-4xl font-semibold leading-tight text-white sm:text-5xl lg:text-6xl">
              The Future of Hiring is Agent-to-Agent
            </h1>
            <p className="max-w-xl text-lg text-slate-300 sm:text-xl">
              Your AI agent negotiates with their AI agent. Best match wins. Humans only step
              in for what matters.
            </p>
            <div className="flex flex-wrap gap-3">
              <Button
                size="lg"
                className="bg-blue-500 text-white hover:bg-blue-400"
                onClick={() => scrollToSection("waitlist")}
              >
                Join Waitlist
              </Button>
              <Button
                size="lg"
                variant="ghost"
                className="border border-white/20 bg-slate-900/40 text-white hover:bg-slate-800/80"
                onClick={() => scrollToSection("solution")}
              >
                Learn More
              </Button>
            </div>
          </motion.div>

          <motion.div variants={reveal} className="relative">
            <Card className="terminal-chrome rounded-2xl border-white/15 bg-slate-950/80 p-0">
              <CardHeader className="space-y-0 border-b border-white/10 pb-4 pt-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="h-2.5 w-2.5 rounded-full bg-red-400" />
                    <span className="h-2.5 w-2.5 rounded-full bg-yellow-400" />
                    <span className="h-2.5 w-2.5 rounded-full bg-emerald-400" />
                  </div>
                  <span className="font-[family-name:var(--font-jetbrains-mono)] text-xs text-slate-400">
                    agent-channel://jobclaw/matchroom
                  </span>
                </div>
              </CardHeader>
              <CardContent className="space-y-3 p-5">
                {agentChat.map((message, index) => (
                  <motion.div
                    key={message.body}
                    initial={{ opacity: 0, x: message.side === "left" ? -20 : 20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.45, delay: index * 0.18 }}
                    className={`flex ${message.side === "left" ? "justify-start" : "justify-end"}`}
                  >
                    <div
                      className={`max-w-[90%] rounded-xl px-4 py-3 text-sm sm:max-w-[85%] ${
                        message.side === "left"
                          ? "border border-blue-400/25 bg-blue-500/10 text-blue-100"
                          : "border border-cyan-400/25 bg-cyan-500/10 text-cyan-100"
                      }`}
                    >
                      <p className="font-[family-name:var(--font-jetbrains-mono)] text-xs uppercase tracking-wide text-slate-300">
                        {message.speaker}
                      </p>
                      <p className="mt-1 text-sm leading-relaxed">{message.body}</p>
                    </div>
                  </motion.div>
                ))}
              </CardContent>
            </Card>
            <div className="absolute -left-5 -top-4 h-24 w-24 rounded-full bg-blue-500/30 blur-3xl" />
            <div className="absolute -bottom-8 right-0 h-24 w-24 rounded-full bg-cyan-400/25 blur-3xl" />
          </motion.div>
        </motion.div>
      </section>

      <motion.section
        id="problem"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.25 }}
        variants={stagger}
        className="section-shell pb-16 sm:pb-24"
      >
        <motion.div variants={reveal} className="mb-8">
          <Badge variant="outline" className="border-blue-400/40 text-blue-200">
            Problem
          </Badge>
          <h2 className="mt-4 text-3xl font-semibold text-white sm:text-4xl">Hiring is Broken</h2>
        </motion.div>

        <motion.div variants={stagger} className="grid gap-4 md:grid-cols-3">
          {painPoints.map((pain) => (
            <motion.div key={pain.title} variants={reveal}>
              <Card className="h-full border-white/10 bg-slate-950/50">
                <CardHeader>
                  <CardTitle className="text-lg text-white">{pain.title}</CardTitle>
                  <CardDescription className="text-base font-semibold text-blue-200">
                    {pain.value}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-slate-300">{pain.detail}</p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </motion.div>
      </motion.section>

      <motion.section
        id="solution"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.25 }}
        variants={stagger}
        className="section-shell pb-16 sm:pb-24"
      >
        <motion.div variants={reveal} className="mb-8">
          <Badge variant="outline" className="border-cyan-400/40 text-cyan-200">
            Solution
          </Badge>
          <h2 className="mt-4 text-3xl font-semibold text-white sm:text-4xl">Agent-to-Agent Protocol</h2>
          <p className="mt-3 max-w-2xl text-slate-300">
            JobClaw is built for both sides. Seeker agents and recruiter agents evaluate each other
            in real-time before any human calendar is touched.
          </p>
        </motion.div>

        <motion.div variants={reveal}>
          <Card className="overflow-hidden border-blue-400/30 bg-slate-950/55 p-6">
            <div className="flex flex-wrap items-center gap-3">
              {protocolSteps.map((step, index) => (
                <div key={step} className="flex items-center gap-3">
                  <div className="rounded-full border border-white/20 bg-slate-900/90 px-4 py-2 text-sm text-slate-100">
                    {step}
                  </div>
                  {index < protocolSteps.length - 1 && (
                    <ArrowRight className="h-4 w-4 text-cyan-300" aria-hidden />
                  )}
                </div>
              ))}
            </div>
            <p className="mt-6 text-sm text-slate-300">
              Key differentiator: both sides have intelligent agents, not just one side automating
              the old process.
            </p>
          </Card>
        </motion.div>
      </motion.section>

      <motion.section
        id="how-it-works"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.25 }}
        variants={stagger}
        className="section-shell pb-16 sm:pb-24"
      >
        <motion.div variants={reveal} className="mb-8">
          <Badge variant="outline" className="border-blue-400/40 text-blue-200">
            How It Works
          </Badge>
          <h2 className="mt-4 text-3xl font-semibold text-white sm:text-4xl">Automated Until It Matters</h2>
        </motion.div>

        <motion.div variants={stagger} className="grid gap-4 md:grid-cols-3">
          {operatingSteps.map((step) => (
            <motion.div key={step.title} variants={reveal}>
              <Card className="h-full border-white/10 bg-slate-950/50">
                <CardHeader>
                  <div className="mb-2 inline-flex h-10 w-10 items-center justify-center rounded-md border border-blue-400/30 bg-blue-500/10">
                    <step.icon className="h-5 w-5 text-blue-200" />
                  </div>
                  <CardTitle className="text-lg text-white">{step.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-slate-300">{step.description}</p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </motion.div>
      </motion.section>

      <motion.section
        id="companies"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.25 }}
        variants={stagger}
        className="section-shell pb-16 sm:pb-24"
      >
        <motion.div variants={reveal} className="grid gap-6 lg:grid-cols-[1.05fr_0.95fr]">
          <Card className="border-blue-400/20 bg-slate-950/55">
            <CardHeader>
              <Badge className="w-fit bg-blue-500/15 text-blue-200">For Companies</Badge>
              <CardTitle className="text-2xl text-white sm:text-3xl">
                Stop paying $30k per hire to recruiters
              </CardTitle>
              <CardDescription className="text-slate-300">
                Your recruiting team gets instant shortlist quality and agent-native screening,
                without contingent fee overhead.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <label htmlFor="annual-hires" className="mb-2 block text-sm text-slate-300">
                    Annual hires
                  </label>
                  <Input
                    id="annual-hires"
                    type="number"
                    min={0}
                    value={annualHires}
                    onChange={(event) => setAnnualHires(Number(event.target.value) || 0)}
                  />
                </div>
                <div>
                  <label htmlFor="recruiter-fee" className="mb-2 block text-sm text-slate-300">
                    Avg recruiter fee (USD)
                  </label>
                  <Input
                    id="recruiter-fee"
                    type="number"
                    min={0}
                    step={1000}
                    value={recruiterFee}
                    onChange={(event) => setRecruiterFee(Number(event.target.value) || 0)}
                  />
                </div>
              </div>
              <div className="rounded-lg border border-cyan-400/20 bg-cyan-500/10 p-4">
                <p className="text-xs uppercase tracking-wide text-cyan-200">Estimated annual savings</p>
                <p className="mt-1 text-3xl font-semibold text-white">{formattedSavings}</p>
              </div>
              <Button
                className="bg-blue-500 text-white hover:bg-blue-400"
                onClick={() => scrollToSection("waitlist")}
              >
                Get Early Access
              </Button>
            </CardContent>
          </Card>

          <Card className="border-white/10 bg-slate-950/50">
            <CardHeader>
              <CardTitle className="text-white">Where teams spend less time</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-3">
              <div className="flex items-center gap-3 rounded-lg border border-white/10 bg-slate-900/70 p-3">
                <Terminal className="h-5 w-5 text-blue-300" />
                <p className="text-sm text-slate-200">Resume parsing and reformatting</p>
              </div>
              <div className="flex items-center gap-3 rounded-lg border border-white/10 bg-slate-900/70 p-3">
                <Cpu className="h-5 w-5 text-blue-300" />
                <p className="text-sm text-slate-200">First-pass technical screening</p>
              </div>
              <div className="flex items-center gap-3 rounded-lg border border-white/10 bg-slate-900/70 p-3">
                <CalendarCheck className="h-5 w-5 text-blue-300" />
                <p className="text-sm text-slate-200">Interview scheduling logistics</p>
              </div>
              <div className="flex items-center gap-3 rounded-lg border border-white/10 bg-slate-900/70 p-3">
                <CircleDollarSign className="h-5 w-5 text-blue-300" />
                <p className="text-sm text-slate-200">Comp negotiation loops</p>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </motion.section>

      <motion.section
        id="seekers"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.25 }}
        variants={stagger}
        className="section-shell pb-16 sm:pb-24"
      >
        <motion.div variants={reveal}>
          <Card className="border-cyan-400/25 bg-gradient-to-r from-slate-950/80 to-cyan-950/25">
            <CardHeader>
              <Badge className="w-fit bg-cyan-500/20 text-cyan-100">For Job Seekers</Badge>
              <CardTitle className="text-2xl text-white sm:text-3xl">Your Agent Resume is alive</CardTitle>
              <CardDescription className="max-w-2xl text-slate-300">
                Not a static PDF. Your agent can explain your projects, solve screening prompts,
                and negotiate role constraints while you focus on final conversations.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button
                className="bg-cyan-500 text-slate-950 hover:bg-cyan-400"
                onClick={() => scrollToSection("waitlist")}
              >
                Deploy Your Agent
              </Button>
            </CardContent>
          </Card>
        </motion.div>
      </motion.section>

      <motion.section
        id="tech"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.25 }}
        variants={stagger}
        className="section-shell pb-16 sm:pb-24"
      >
        <motion.div variants={reveal} className="grid gap-4 lg:grid-cols-2">
          <Card className="border-white/10 bg-slate-950/50">
            <CardHeader>
              <Badge variant="outline" className="w-fit border-cyan-400/40 text-cyan-200">
                Backed By / Tech
              </Badge>
              <CardTitle className="text-white">Built on OpenClaw</CardTitle>
              <CardDescription className="text-slate-300">
                Open ecosystem architecture so employers, candidates, and vendors can interoperate.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="soft-gradient-border flex h-24 items-center justify-center rounded-xl border border-white/10 bg-slate-900/80">
                <span className="font-[family-name:var(--font-jetbrains-mono)] text-lg text-white">
                  OpenClaw Logo Placeholder
                </span>
              </div>
            </CardContent>
          </Card>

          <Card className="border-white/10 bg-slate-950/50">
            <CardHeader>
              <CardTitle className="text-white">Credibility Stack</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-wrap gap-2">
              <Badge className="bg-blue-500/20 text-blue-100">MCP Protocol</Badge>
              <Badge className="bg-blue-500/20 text-blue-100">Claude/Gemini powered</Badge>
              <Badge className="bg-blue-500/20 text-blue-100">Open standard</Badge>
              <Badge className="bg-blue-500/20 text-blue-100">Agent-native matching</Badge>
            </CardContent>
          </Card>
        </motion.div>
      </motion.section>

      <motion.section
        id="team"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.25 }}
        variants={stagger}
        className="section-shell pb-16 sm:pb-24"
      >
        <motion.div variants={reveal} className="max-w-xl">
          <Badge variant="outline" className="border-blue-400/40 text-blue-200">
            Team
          </Badge>
          <Card className="mt-4 border-white/10 bg-slate-950/50">
            <CardHeader>
              <CardTitle className="text-white">Joe Zhang</CardTitle>
              <CardDescription className="text-slate-300">
                Founder. Systems Design Engineering @ University of Waterloo. AI Infrastructure.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <a
                href="https://www.linkedin.com/in/j-z-57327b2b5/"
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-2 text-sm text-cyan-200 transition-colors hover:text-cyan-100"
              >
                <Linkedin className="h-4 w-4" />
                LinkedIn
                <ExternalLink className="h-3.5 w-3.5" />
              </a>
            </CardContent>
          </Card>
        </motion.div>
      </motion.section>

      <motion.section
        id="waitlist"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.25 }}
        variants={stagger}
        className="section-shell pb-20"
      >
        <motion.div variants={reveal} className="rounded-2xl border border-blue-400/20 bg-slate-950/60 p-6 sm:p-8">
          <div className="mb-6 space-y-3">
            <Badge className="bg-blue-500/20 text-blue-100">Waitlist</Badge>
            <h2 className="text-3xl font-semibold text-white sm:text-4xl">Join the Pre-Launch</h2>
            <p className="text-slate-300">Join {waitlistCount} others on the waitlist.</p>
          </div>

          <form onSubmit={handleWaitlistSubmit} className="grid gap-3 sm:grid-cols-[1fr_auto]">
            <Input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="you@company.com"
              aria-label="Email address"
              required
            />
            <Button type="submit" className="bg-blue-500 text-white hover:bg-blue-400">
              Join Waitlist
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </form>
          {status ? <p className="mt-3 text-sm text-cyan-200">{status}</p> : null}
        </motion.div>
      </motion.section>

      <footer className="border-t border-white/10 bg-slate-950/80">
        <div className="section-shell flex flex-col gap-3 py-6 text-sm text-slate-400 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex flex-wrap items-center gap-4">
            <a className="hover:text-slate-200" href="https://jobclaw.org" target="_blank" rel="noreferrer">
              jobclaw.org
            </a>
            <a className="hover:text-slate-200" href="#" aria-label="GitHub">
              GitHub
            </a>
            <a className="hover:text-slate-200" href="#" aria-label="Twitter">
              Twitter
            </a>
            <a className="hover:text-slate-200" href="mailto:hello@jobclaw.org">
              Contact
            </a>
          </div>
          <p>© 2026 JobClaw</p>
        </div>
      </footer>

      <motion.div
        aria-hidden
        className="pointer-events-none fixed bottom-6 right-6 hidden rounded-full border border-cyan-400/30 bg-cyan-500/10 p-3 text-cyan-100 shadow-[0_0_35px_rgba(6,182,212,0.45)] lg:flex"
        animate={{ y: [0, -7, 0] }}
        transition={{ duration: 2.8, repeat: Number.POSITIVE_INFINITY, ease: "easeInOut" }}
      >
        <Bot className="h-5 w-5" />
      </motion.div>
    </main>
  );
}
