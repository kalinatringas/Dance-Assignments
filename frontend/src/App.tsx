import { useState } from 'react'
import axios from 'axios'
import './App.css'

function App() {
  const [dancersFile, setDancersFile] = useState<File | null>(null);
  const [dancesFile, setDancesFile] = useState<File | null>(null);
  const [result, setResult] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit= async() =>{
    if (!dancersFile || !dancesFile){
      alert("Please input both files!");
      return;
    }

    const formData = new FormData();
    formData.append("dancers_csv", dancersFile)
    formData.append("dances_csv", dancesFile)

      setLoading(true);
      try{
        const url = "http://localhost:8000/generate";
        console.log("Posting to", url);
        const res = await axios.post(url, formData);
        let payload = res.data;
        if (Array.isArray(payload)) {
          // Keep as-is; frontend will show the best (first) and allow viewing others if needed
          setResult({ configs: payload });
        } else if (payload.configs) {
          setResult(payload);
        } else {
          // single object response (maybe {message: ...})
          setResult(payload);
        }
      }catch(err:any){
        console.error("Axios error:", err);
        if (err.response){
          console.error("Response status:", err.response.status);
          console.error("Response data:", err.response.data);
          alert(`Request failed: ${err.response.status} - ${JSON.stringify(err.response.data)}`)
        } else {
          alert(`Network Error: ${err.message}`)
        }
      }finally{
        setLoading(false);
      }
  };



  return (
    <>
     <div className="p-10 text-center">
      <h1 className="text-2xl font-bold mb-4">Dance Scheduler</h1>

      <input
        type="file"
        accept=".csv"
        onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
          const f = e.target.files && e.target.files[0] ? e.target.files[0] : null;
          setDancersFile(f);
        }}
      />
      <input
        type="file"
        accept=".csv"
        onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
          const f = e.target.files && e.target.files[0] ? e.target.files[0] : null;
          setDancesFile(f);
        }}
        className="ml-2"
      />
      <button
        onClick={handleSubmit}
        disabled={loading}
        className="bg-blue-500 text-white px-4 py-2 rounded ml-2"
      >
        {loading ? "Generating..." : "Generate"}
      </button>
        
      {result && (
        <div className="mt-6 text-left">
          {/* If multiple configs are returned, render each one */}
          {result.configs && result.configs.length > 0 ? (
            result.configs.map((cfg: any, idx: number) => (
              <div key={idx} className="mb-8">
                <h2 className="text-xl font-semibold">Configuration {idx + 1} - Satisfaction Score: {cfg.satisfaction}</h2>
                <h3 className='text-l font-semibold'>Violations: {cfg.violations}</h3>
                
                {cfg.assignments_by_dance ? (
                  <div>
                    <h3 className="text-lg font-medium mt-2">Assignments by Dance</h3>
                    <div className="bg-pink-100 p-4 rounded text-left mt-2 ">
                      {Object.keys(cfg.assignments_by_dance).sort().map((dance) => (
                        <div key={dance} className="mb-2">
                          <strong>{dance}</strong>
                          <ul className="list-disc ml-4">
                            {cfg.assignments_by_dance[dance].map((d: string) => (
                              <li className="text-left" key={d}>{d}</li>
                            ))}
                          </ul>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                    <pre className="bg-gray-100 p-4 rounded text-left mt-2">{JSON.stringify(cfg.assignments, null, 2)}</pre>
                )}

                <h3 className="text-lg font-medium mt-4">Report</h3>
                <pre className="bg-black text-white p-4 rounded text-left mt-2 w-[100vw] whitespace-pre-wrap">{cfg.report_text}</pre>
              </div>
            ))
          ) : result.satisfaction ? (
            // single-result object with satisfaction
            <div>
              <h2 className="text-xl font-semibold">Satisfaction Score: {result.satisfaction}</h2>
                <pre className="bg-gray-100 p-4 rounded text-left mt-2">{JSON.stringify(result.assignments, null, 2)}</pre>
              <h3 className="text-lg font-medium mt-4">Report</h3>
              <pre className="bg-black text-white p-4 rounded text-left mt-2 w-[100vw] whitespace-pre-wrap">{result.report_text}</pre>
            </div>
          ) : (
            // fallback: show raw response
            <div></div>
           // <pre className="bg-red-100 p-4 rounded text-left mt-2 w-[100vw]">{JSON.stringify(result, null, 2)}</pre>
          )}
        </div>
      )}
    </div>
    </>
  )
}

export default App
