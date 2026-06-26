"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useState, FormEvent, useEffect } from "react";
import { 
  ShoppingBag, 
  Info, 
  FileCode2, 
  RotateCw, 
  RefreshCcw, 
  MoreVertical,
  Search,
  Laptop,
  Smartphone,
  Headphones,
  Watch,
  Camera,
  Briefcase,
  Loader2,
  ExternalLink
} from "lucide-react";

export default function Home() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any[]>([]);
  const [hasSearched, setHasSearched] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const categories = [
    { name: "Laptops", id: "laptops", icon: Laptop, iconClass: "text-purple-accent" },
    { name: "Smartphones", id: "smartphones", icon: Smartphone, iconClass: "text-cyan-accent" },
    { name: "Headphones", id: "headphones", icon: Headphones, iconClass: "text-pink-accent" },
    { name: "Smartwatches", id: "smartwatches", icon: Watch, iconClass: "text-purple-accent" },
    { name: "Cameras", id: "cameras", icon: Camera, iconClass: "text-cyan-accent" },
    { name: "Accessories", id: "accessories", icon: Briefcase, iconClass: "text-pink-accent" },
  ];

  const handleSearch = async (e?: FormEvent, directCategory?: string) => {
    if (e) e.preventDefault();
    const searchQuery = directCategory ? `Top rated ${directCategory}` : query;
    if (!searchQuery.trim()) return;

    if (directCategory) {
      setQuery(searchQuery);
    }

    setLoading(true);
    setHasSearched(true);
    
    try {
      const response = await fetch("http://localhost:8002/api/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          query: searchQuery, 
          direct_category: directCategory || null 
        }),
      });
      
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      
      const data = await response.json();
      setResults(data.recommendations || []);
    } catch (error) {
      console.error("Search failed:", error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-navy-900 text-foreground overflow-x-hidden relative selection:bg-purple-accent/30">
      {/* Background Gradients & Grid */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <div className="absolute top-[-10%] left-1/2 -translate-x-1/2 w-[1000px] h-[600px] opacity-30 rounded-[100%] bg-[radial-gradient(ellipse_at_center,_var(--color-purple-accent),_var(--color-navy-800),_transparent)] blur-3xl mix-blend-screen" />
        <div className="absolute top-[20%] left-[-10%] w-[500px] h-[500px] opacity-20 rounded-[100%] bg-[radial-gradient(ellipse_at_center,_var(--color-cyan-accent),_transparent)] blur-3xl mix-blend-screen" />
        <div className="absolute bottom-[10%] right-[-10%] w-[600px] h-[600px] opacity-20 rounded-[100%] bg-[radial-gradient(ellipse_at_center,_var(--color-pink-accent),_transparent)] blur-3xl mix-blend-screen" />
        <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:64px_64px] [mask-image:radial-gradient(ellipse_80%_80%_at_50%_100%,#000_20%,transparent_100%)]" />
      </div>

      {/* Floating Particles Animation */}
      <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden">
        {mounted && [...Array(20)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1 h-1 bg-white/20 rounded-full"
            initial={{
              x: typeof window !== 'undefined' ? Math.random() * window.innerWidth : Math.random() * 1000,
              y: typeof window !== 'undefined' ? Math.random() * window.innerHeight : Math.random() * 1000,
            }}
            animate={{
              y: [null, Math.random() * -500],
              opacity: [0, 1, 0],
            }}
            transition={{
              duration: Math.random() * 10 + 10,
              repeat: Infinity,
              ease: "linear",
            }}
          />
        ))}
      </div>

      {/* Navbar */}
      <nav className="fixed top-0 left-0 right-0 z-50 px-6 py-4 border-b border-white/5 bg-navy-900/40 backdrop-blur-md">
        <div className="max-w-[1400px] mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="bg-purple-accent p-2 rounded-lg shadow-[0_0_15px_rgba(139,92,246,0.4)]">
              <ShoppingBag className="w-5 h-5 text-white" />
            </div>
            <span className="font-semibold text-lg tracking-tight">AI Shopping Advisor</span>
          </div>
          
          <div className="hidden md:flex items-center gap-6 text-sm text-slate-300 font-medium">
            <button className="flex items-center gap-2 hover:text-white transition-colors">
              <Info className="w-4 h-4" /> Info
            </button>
            <button className="flex items-center gap-2 hover:text-white transition-colors">
              <FileCode2 className="w-4 h-4" /> File change
            </button>
            <button className="flex items-center gap-2 hover:text-white transition-colors">
              <RotateCw className="w-4 h-4" /> Rerun
            </button>
            <button className="flex items-center gap-2 hover:text-white transition-colors">
              <RefreshCcw className="w-4 h-4" /> Always rerun
            </button>
            <button className="hover:text-white transition-colors">
              <MoreVertical className="w-4 h-4" />
            </button>
          </div>
        </div>
      </nav>

      <div className="relative z-10 max-w-[1400px] mx-auto px-6 pt-32 pb-20 flex flex-col items-center">
        
        {/* Hero Section */}
        <motion.div 
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="flex flex-col items-center text-center mt-12 w-full"
        >
          <motion.div 
            animate={{ y: [0, -10, 0] }}
            transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
            className="flex items-center gap-2 px-4 py-1.5 rounded-full border border-purple-accent/20 bg-purple-accent/10 backdrop-blur-sm text-purple-accent/90 text-sm font-medium mb-8 shadow-[0_0_20px_rgba(139,92,246,0.15)] cursor-default"
          >
            <span className="text-base">✨</span> Powered by Gemini 3.1 & LangGraph
          </motion.div>

          <h1 className="text-5xl md:text-[72px] font-extrabold tracking-tight leading-[1.1] mb-6 drop-shadow-[0_0_40px_rgba(139,92,246,0.4)]">
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-accent to-pink-accent">
              AI Shopping Advisor
            </span>
          </h1>

          <p className="text-lg md:text-xl text-slate-400 max-w-2xl font-light tracking-wide mb-6">
            Discover the perfect product with the power of AI.
          </p>

          <div className="flex flex-wrap justify-center gap-4 text-sm font-medium text-slate-300">
            <span className="flex items-center gap-1.5">🔍 Smart Search</span>
            <span className="text-slate-600">•</span>
            <span className="flex items-center gap-1.5">✦ AI Recommendations</span>
            <span className="text-slate-600">•</span>
            <span className="flex items-center gap-1.5">🏷 Best Deals</span>
          </div>
        </motion.div>

        {/* Search Bar */}
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="w-full max-w-[1000px] mt-16 mb-16"
        >
          <form onSubmit={handleSearch} className="relative group rounded-[24px] bg-navy-800/60 backdrop-blur-xl border border-purple-accent/30 shadow-[0_0_40px_-10px_rgba(139,92,246,0.3)] transition-all duration-300 hover:shadow-[0_0_60px_-15px_rgba(139,92,246,0.5)] hover:border-purple-accent/50 p-3 pl-6 flex items-center">
            <Search className="w-6 h-6 text-slate-400 mr-4 shrink-0" />
            <input 
              type="text" 
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="E.g., Find me a cheap laptop under 500 dollars..." 
              className="w-full bg-transparent border-none outline-none text-lg text-white placeholder:text-slate-500 font-medium h-14"
              disabled={loading}
            />
            <button 
              type="submit"
              disabled={loading}
              className="shrink-0 flex items-center justify-center gap-2 bg-gradient-to-r from-purple-accent to-pink-accent text-white px-8 py-4 rounded-[16px] font-semibold tracking-wide hover:scale-[1.02] active:scale-[0.98] transition-all shadow-[0_0_20px_rgba(217,70,239,0.4)] disabled:opacity-70 disabled:hover:scale-100"
            >
              {loading ? (
                <><Loader2 className="w-5 h-5 animate-spin" /> Analyzing...</>
              ) : (
                "Search Products →"
              )}
            </button>
          </form>
        </motion.div>

        {/* Results Section */}
        <AnimatePresence>
          {hasSearched && (
            <motion.div 
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="w-full max-w-[1200px] mb-16"
            >
              {loading ? (
                <div className="flex flex-col items-center justify-center py-20 text-slate-400">
                  <div className="relative">
                    <div className="absolute inset-0 blur-xl bg-purple-accent/30 rounded-full animate-pulse" />
                    <Loader2 className="w-12 h-12 animate-spin text-purple-accent relative z-10" />
                  </div>
                  <p className="mt-6 text-lg font-medium animate-pulse">AI is finding the best matches...</p>
                </div>
              ) : results.length > 0 ? (
                <div>
                  <h3 className="text-2xl font-bold text-white mb-8 border-b border-white/10 pb-4 inline-block">
                    Top Recommendations
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {results.map((product, idx) => (
                      <motion.div 
                        key={idx}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: idx * 0.1 }}
                        className="bg-navy-800/50 backdrop-blur-md rounded-2xl border border-purple-accent/30 overflow-hidden hover:border-purple-accent/60 hover:shadow-[0_0_30px_rgba(139,92,246,0.15)] transition-all duration-300 flex flex-col"
                      >
                        <div className="p-6 flex-1 flex flex-col">
                          <div className="text-xs uppercase font-bold text-purple-accent tracking-wider mb-2">
                            {product.category || "Uncategorized"}
                          </div>
                          <h4 className="text-lg font-semibold text-white mb-4 line-clamp-2">
                            {product.name}
                          </h4>
                          <div className="text-3xl font-extrabold text-cyan-accent mb-6">
                            ${product.price_usd}
                          </div>
                          <div className="bg-navy-900/50 p-4 rounded-xl border border-white/5 mt-auto">
                            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">
                              Why we picked this
                            </span>
                            <p className="text-sm text-slate-300 leading-relaxed">
                              {product.justification || "Matches your preferences closely."}
                            </p>
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="text-center py-20 bg-navy-800/30 rounded-3xl border border-white/5">
                  <span className="text-4xl mb-4 block">😕</span>
                  <h3 className="text-xl font-semibold text-white mb-2">No products found</h3>
                  <p className="text-slate-400">Try adjusting your search query or budget.</p>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Popular Categories */}
        <div className="w-full mt-8">
          <h2 className="text-center text-xl font-semibold text-white mb-10 tracking-wide drop-shadow-md">Popular Categories</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-6">
            {categories.map((category, i) => (
              <motion.div
                key={category.name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.3 + i * 0.1 }}
                whileHover={{ y: -8, scale: 1.03 }}
                onClick={() => handleSearch(undefined, category.id)}
                className="group cursor-pointer flex flex-col items-center justify-center p-8 bg-navy-800/40 backdrop-blur-md rounded-[20px] border border-white/5 hover:border-purple-accent/40 transition-all duration-300 hover:shadow-[0_15px_40px_-10px_rgba(139,92,246,0.4)] hover:bg-navy-800/80"
              >
                <category.icon className={`w-10 h-10 mb-4 ${category.iconClass} drop-shadow-[0_0_15px_currentColor] transition-transform duration-300 group-hover:scale-110`} />
                <h3 className="font-semibold text-white mb-2">{category.name}</h3>
                <span className="text-xs text-slate-400 font-medium group-hover:text-white transition-colors opacity-0 group-hover:opacity-100 -translate-y-2 group-hover:translate-y-0 duration-300">
                  Explore Now →
                </span>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Features Section */}
        <motion.div 
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.8 }}
          className="w-full mt-24 bg-navy-800/30 backdrop-blur-xl rounded-[24px] border border-purple-accent/20 shadow-[0_0_50px_-20px_rgba(139,92,246,0.15)] p-0 overflow-hidden relative"
        >
          <div className="absolute inset-0 bg-gradient-to-b from-purple-accent/5 to-transparent pointer-events-none" />
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-0 divide-y md:divide-y-0 md:divide-x divide-white/10 relative z-10">
            <div className="flex flex-col items-center text-center p-10 md:p-12 hover:bg-white/5 transition-colors duration-300">
              <span className="text-3xl mb-4 drop-shadow-[0_0_10px_rgba(255,255,255,0.5)]">✨</span>
              <h4 className="text-lg font-bold text-white mb-3 tracking-wide">AI-Powered Search</h4>
              <p className="text-slate-400 text-sm leading-relaxed max-w-[250px]">
                Get intelligent product recommendations tailored to your needs.
              </p>
            </div>
            
            <div className="flex flex-col items-center text-center p-10 md:p-12 hover:bg-white/5 transition-colors duration-300">
              <span className="text-3xl mb-4 drop-shadow-[0_0_10px_rgba(255,255,255,0.5)]">⚡</span>
              <h4 className="text-lg font-bold text-white mb-3 tracking-wide">Real-time Information</h4>
              <p className="text-slate-400 text-sm leading-relaxed max-w-[250px]">
                Access up-to-date prices, reviews, and product availability.
              </p>
            </div>

            <div className="flex flex-col items-center text-center p-10 md:p-12 hover:bg-white/5 transition-colors duration-300">
              <span className="text-3xl mb-4 drop-shadow-[0_0_10px_rgba(255,255,255,0.5)]">⚖</span>
              <h4 className="text-lg font-bold text-white mb-3 tracking-wide">Smart Comparisons</h4>
              <p className="text-slate-400 text-sm leading-relaxed max-w-[250px]">
                Compare products easily and find the best value for your money.
              </p>
            </div>
          </div>
        </motion.div>

        {/* Footer */}
        <footer className="mt-24 w-full text-center pb-8">
          <p className="text-sm text-slate-500 font-medium">
            Built with LangGraph, PostgreSQL, and Google Gemini 💜
          </p>
        </footer>

      </div>
    </main>
  );
}
