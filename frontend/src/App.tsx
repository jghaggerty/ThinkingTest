import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from '@/components/ui/toaster';
import { Toaster as Sonner } from '@/components/ui/sonner';
import { TooltipProvider } from '@/components/ui/tooltip';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import CreateEvaluation from './pages/CreateEvaluation';
import EvaluationDetail from './pages/EvaluationDetail';
import BiasAnalysis from './pages/BiasAnalysis';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <Router>
          <Routes>
            <Route path="/" element={<Layout><Dashboard /></Layout>} />
            <Route path="/create" element={<Layout><CreateEvaluation /></Layout>} />
            <Route path="/evaluations/:id" element={<Layout><EvaluationDetail /></Layout>} />
            <Route path="/bias-analysis" element={<BiasAnalysis />} />
          </Routes>
        </Router>
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;
