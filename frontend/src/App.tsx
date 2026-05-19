

import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Navbar } from './components/Navbar';
import { Home } from './pages/Home';
import { Graph } from './pages/Graph';
import { Architecture } from './pages/Architecture';
import { Process } from './pages/Process';
import { Status } from './pages/Status';
import { Query } from './pages/Query';

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-950">
        <Navbar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/graph" element={<Graph />} />
          <Route path="/architecture" element={<Architecture />} />
          <Route path="/process" element={<Process />} />
          <Route path="/status" element={<Status />} />
          <Route path="/query" element={<Query />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
