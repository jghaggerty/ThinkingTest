import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import CreateEvaluation from './pages/CreateEvaluation';
import EvaluationDetail from './pages/EvaluationDetail';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/create" element={<CreateEvaluation />} />
          <Route path="/evaluations/:id" element={<EvaluationDetail />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
