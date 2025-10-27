import { useState } from 'react'
import { UploadSection } from './ui/UploadSection';
import axios from 'axios'
import { Card} from "@/components/ui/card"
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "@/components/ui/carousel"

//import 'bootstrap/dist/css/bootstrap.min.css'
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
    
    <div className="min-w-[90%] max-w-screen text-black/80 p-10 text-center"> 
      <h1 className="text-2xl font-bold m-auto justify-around pb-3 mb-0.5 font-motley">Dance Scheduler</h1>
      <h3 className = "font-sans mb-1 ">Gone are the days of playing the impossible balancing game when placing dancers into dances!</h3>
      <div className='grid grid-cols-2 gap-4 mx-auto mb-8 max-w-4xl'>
        <UploadSection
          title= 'Dance Choices'
          description='Upload a csv of the dancers ranked choices'
          file = {dancersFile}
          onFileChange={setDancersFile}
          color='blue'
          icon = '😈'
        />
        <UploadSection
          title = 'Dances'
          description='Upload a csv of the dances, and their spots'
          file = {dancesFile}
          onFileChange={setDancesFile}
          color = 'blue'
          icon = '😼'
        />
      </div>
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
        <Carousel
        opts={{
        align: "start",
        }}
        
        >
        <CarouselContent >
          {result.configs && result.configs.length > 0 ? (
            result.configs.map((cfg: any, idx: number) => (
              <CarouselItem key={idx} className="mb-0 m-auto text-center w-full">
                <Card className='bg-purple-200/20 border-white/20'>
                <h2 className="text-xl font-semibold mb-0">Configuration {idx + 1} - Satisfaction Score: {cfg.satisfaction}</h2>
                <h3 className='text-m font-semibold m-6 mt-0 mb-0'>Violations: {cfg.violations}</h3>                
                {cfg.assignments_by_dance ? (
                  <div>
                    <h3 className="text-lg font-medium mt-0 m-auto">Assignments by Dance</h3>
                    <div className='grid grid-flow-col'>
                      {Object.keys(cfg.assignments_by_dance).sort().map((dance) => (
                        <div key={dance} className="m-auto text-center bg-purple-100/80 p-4 rounded-xl max-w-fit mt-2">
                          <strong className='text-m'>{dance}</strong>
                          <div>---------------</div>
                          <div/>
                          <div className="m-auto pink text-center">
                            {cfg.assignments_by_dance[dance].map((d: string) => (
                              <div className="text-center m-auto " key={d}>{d}</div>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                 
                ) : (
                  <pre className="bg-gray-100 p-4 rounded text-left mt-2 w-screen">{JSON.stringify(cfg.assignments, null, 2)}</pre>
                )}
                </Card> 
                </CarouselItem> 
                    
            ))
          ) : result.satisfaction ? (
            // single-result object with satisfaction
            <div>
              <h2 className="text-xl font-semibold">Satisfaction Score: {result.satisfaction}</h2>
              <pre className="bg-gray-100 p-4 rounded text-left mt-2 w-screen">{JSON.stringify(result.assignments, null, 2)}</pre>
              <pre className="bg-black text-white p-4 rounded text-left mt-2 w-screen whitespace-pre-wrap">{result.report_text}</pre>
            </div>
          ) : (
            // fallback: show raw response
            <div></div>
           // <pre className="bg-red-100 p-4 rounded text-left mt-2 w-[100vw]">{JSON.stringify(result, null, 2)}</pre>
          )}
          </CarouselContent>   
          <CarouselPrevious className='bg-purple-200'/>
          <CarouselNext className='bg-purple-400'/>
          </Carousel>
        </div>
      )}
    </div>
    </>
  )
}

export default App
