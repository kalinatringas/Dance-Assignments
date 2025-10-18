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
        setResult(res.data);
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
        <div className="mt-6">
          <h2 className="text-xl font-semibold">
            Satisfaction Score: {result.satisfaction}
          </h2>
          <pre className="bg-gray-100 p-4 rounded text-left mt-2 w-[100vw]">
            {JSON.stringify(result.assignments, null, 2)}
          </pre>
        </div>
      )}
    </div>
    </>
  )
}

export default App
