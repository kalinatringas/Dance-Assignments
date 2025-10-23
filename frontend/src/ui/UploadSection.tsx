import { useRef } from 'react';
import { Upload, FileText, X } from 'lucide-react';

interface UploadSectionProps {
  title: string;
  description: string;
  file: File | null;
  onFileChange: (file: File | null) => void;
  icon: string;
  color: 'blue' | 'purple';
}

export function UploadSection({ title, description, file, onFileChange, icon, color }: UploadSectionProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && droppedFile.type === 'text/csv') {
      onFileChange(droppedFile);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      onFileChange(selectedFile);
    }
  };

  const handleRemove = () => {
    onFileChange(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    } 
  };

  const bgColor = color === 'blue' ? 'bg-blue-50/50' : 'bg-purple-50/50';
  const borderColor = color === 'blue' ? 'border-blue-300' : 'border-purple-300';
  const textColor = color === 'blue' ? 'text-blue-600' : 'text-purple-600';
  const buttonBg = color === 'blue' ? 'bg-blue-500 hover:bg-blue-600' : 'bg-purple-500 hover:bg-purple-600';

  return (
    <div className={`${bgColor} backdrop-blur-sm rounded-3xl p-6 shadow-lg border-2 border-dashed ${borderColor} transition-all hover:shadow-xl`}>
      <div className="text-center mb-4">
        <div className="text-4xl mb-2">{icon}</div>
        <h3 className={textColor}>{title}</h3>
        <p className="text-gray-600 text-sm">{description}</p>
      </div>

      {!file ? (
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          className="border-2 border-dashed border-gray-300 rounded-2xl p-8 text-center cursor-pointer hover:border-gray-400 transition-all"
          onClick={() => fileInputRef.current?.click()}
        >
          <Upload className="w-12 h-12 mx-auto mb-3 text-gray-400" />
          <p className="text-gray-600 mb-2">Drag & drop your CSV here</p>
          <p className="text-gray-400 text-sm mb-3">or</p>
          <button className={`${buttonBg} text-white px-6 py-2 rounded-full transition-colors`}>
            Browse Files
          </button>
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv"
            onChange={handleFileSelect}
            className="hidden"
          />
        </div>
      ) : (
        <div className="bg-white rounded-2xl p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <FileText className={`w-8 h-8 ${textColor}`} />
            <div>
              <p className="text-gray-800">{file.name}</p>
              <p className="text-gray-500 text-sm">{(file.size / 1024).toFixed(2)} KB</p>
            </div>
          </div>
          <button
            onClick={handleRemove}
            className="text-gray-400 hover:text-red-500 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      )}
    </div>
  );
}
