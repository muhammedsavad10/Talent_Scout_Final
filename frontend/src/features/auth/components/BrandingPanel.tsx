import React from 'react';
import { motion } from 'framer-motion';
import { BrainCircuit, Target, Sparkles, Layout, Lock } from 'lucide-react';

const FEATURES = [
  {
    icon: BrainCircuit,
    title: 'AI Resume Intelligence',
    description: 'Multi-modal candidate parsing with structural entity extraction and skill verification.',
    accent: 'text-indigo-400',
    bg: 'bg-indigo-500/10 border-indigo-500/20',
  },
  {
    icon: Target,
    title: 'Semantic Candidate Matching',
    description: 'Role-aware vector scoring, experience alignment, and competency benchmarking.',
    accent: 'text-purple-400',
    bg: 'bg-purple-500/10 border-purple-500/20',
  },
  {
    icon: Sparkles,
    title: 'Explainable AI (XAI)',
    description: 'Deterministic evidence lineage, transparent scoring formulas, and recruiter insights.',
    accent: 'text-cyan-400',
    bg: 'bg-cyan-500/10 border-cyan-500/20',
  },
];

export const BrandingPanel: React.FC = () => {
  return (
    <div className="flex flex-col justify-between space-y-8 py-2">
      {/* Top Header Logo */}
      <motion.div
        initial={{ opacity: 0, y: -12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="flex items-center gap-3"
      >
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 p-0.5 shadow-md shadow-indigo-500/20">
          <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
            <Layout className="w-5 h-5 text-indigo-400" />
          </div>
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold tracking-tight text-white">TalentScout</h2>
            <span className="px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 rounded-md">
              Enterprise
            </span>
          </div>
          <p className="text-xs text-slate-400 font-medium">AI Recruitment Intelligence Platform</p>
        </div>
      </motion.div>

      {/* Hero Headline Section */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="space-y-6"
      >
        <div className="space-y-3">
          <h1 className="text-3xl sm:text-4xl xl:text-5xl font-extrabold tracking-tight text-white leading-tight">
            Discover, Evaluate & <br className="hidden sm:inline" />
            <span className="bg-gradient-to-r from-indigo-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent">
              Hire Top Talent with AI.
            </span>
          </h1>
          <p className="text-sm sm:text-base text-slate-400 leading-relaxed max-w-lg">
            Automate candidate evaluations with multi-provider LLM swarms, 
            deterministic scoring models, and explainable recruiter rationale.
          </p>
        </div>

        {/* Real Dashboard Feature Cards */}
        <div className="space-y-3.5">
          {FEATURES.map((feature, idx) => {
            const Icon = feature.icon;
            return (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, x: -16 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.4, delay: 0.2 + idx * 0.1 }}
                whileHover={{ y: -2 }}
                className="p-4 sm:p-5 rounded-2xl border border-slate-800/90 bg-slate-900/60 backdrop-blur-md transition-all duration-200 shadow-sm hover:border-slate-700 hover:shadow-md group"
              >
                <div className="flex items-start gap-4">
                  <div className={`p-2.5 rounded-xl ${feature.bg} ${feature.accent} shrink-0 mt-0.5`}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-white group-hover:text-indigo-300 transition-colors">
                      {feature.title}
                    </h3>
                    <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                      {feature.description}
                    </p>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      </motion.div>

      {/* Footer Security Badge */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.4, delay: 0.5 }}
        className="pt-4 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400"
      >
        <div className="flex items-center gap-2">
          <Lock className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>Encrypted Session & Access Tokens Protected</span>
        </div>
        <span className="font-mono text-[11px] text-slate-500">v1.0.0-PROD</span>
      </motion.div>
    </div>
  );
};

export default BrandingPanel;
