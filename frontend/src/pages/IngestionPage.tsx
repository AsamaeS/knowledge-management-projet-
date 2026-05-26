import React, { useState, useEffect } from 'react';
import { listDocuments, ingestFile } from '../api/ingestion';
import { Document } from '../types';
import { UploadCloud, CheckCircle, AlertCircle, FileText, Calendar, User, Database } from 'lucide-react';

export default function IngestionPage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [sourceType, setSourceType] = useState<string>('interview');
  const [author, setAuthor] = useState<string>('');
  const [docDate, setDocDate] = useState<string>('');
  
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [uploadStatus, setUploadStatus] = useState<{ success: boolean; msg: string } | null>(null);
  const [isLoadingDocs, setIsLoadingDocs] = useState<boolean>(false);

  const fetchDocs = async () => {
    setIsLoadingDocs(true);
    try {
      const data = await listDocuments(30, 0);
      setDocuments(data);
    } catch (err: any) {
      console.error(err);
    } finally {
      setIsLoadingDocs(false);
    }
  };

  useEffect(() => {
    fetchDocs();
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
      setUploadStatus(null);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setIsUploading(true);
    setUploadStatus(null);

    try {
      const res = await ingestFile(file, sourceType, author || undefined, docDate || undefined);
      setUploadStatus({
        success: true,
        msg: `Successfully indexed! Created ${res.chunk_count} chunks, extracted ${res.entities_extracted} entities and ${res.edges_created} relationships.`
      });
      setFile(null);
      setAuthor('');
      setDocDate('');
      fetchDocs();
    } catch (err: any) {
      setUploadStatus({
        success: false,
        msg: err.message || 'Ingestion failed. Please check your file type or API server.'
      });
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8 pb-16">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-slate-100 to-slate-400 bg-clip-text text-transparent">
          Document Ingestion Portal
        </h1>
        <p className="text-slate-400 mt-2">
          Ingest strategic intelligence files to split them into vector chunks and populate the NEXUS Knowledge Graph.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Upload Form Panel Left */}
        <div className="lg:col-span-1 bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 h-fit shadow-xl shadow-slate-950/20">
          <h2 className="text-lg font-bold text-slate-200 mb-6 flex items-center space-x-2">
            <UploadCloud className="w-5 h-5 text-indigo-500" />
            <span>Upload Dataset File</span>
          </h2>
          
          <form onSubmit={handleUpload} className="space-y-5">
            {/* Dropzone */}
            <div className="border-2 border-dashed border-slate-800 hover:border-indigo-500/50 transition-colors duration-200 rounded-xl p-6 text-center cursor-pointer relative bg-slate-950/50">
              <input
                type="file"
                accept=".pdf,.docx,.txt,.json,.csv"
                onChange={handleFileChange}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                required
              />
              <UploadCloud className="w-10 h-10 mx-auto text-slate-500 mb-2" />
              {file ? (
                <div className="space-y-1">
                  <p className="text-sm font-medium text-slate-300 truncate max-w-xs">{file.name}</p>
                  <p className="text-xs text-slate-500 font-mono">{(file.size / 1024).toFixed(1)} KB</p>
                </div>
              ) : (
                <div className="space-y-1">
                  <p className="text-sm font-medium text-slate-400">Drag & drop or click to choose</p>
                  <p className="text-xs text-slate-600">Supports PDF, DOCX, TXT, JSON, CSV</p>
                </div>
              )}
            </div>

            {/* Source Type */}
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Source Classification</label>
              <select
                value={sourceType}
                onChange={(e) => setSourceType(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-200 focus:outline-none focus:border-indigo-500 transition-colors duration-200"
              >
                <option value="interview">Expert Interview</option>
                <option value="report">Field Report</option>
                <option value="linkedin">LinkedIn Post</option>
                <option value="analysis">Strategic Analysis</option>
              </select>
            </div>

            {/* Optional Author */}
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Author (Optional)</label>
              <div className="relative">
                <User className="absolute left-4 top-3.5 w-4 h-4 text-slate-500" />
                <input
                  type="text"
                  placeholder="e.g. Dr. Jane Doe"
                  value={author}
                  onChange={(e) => setAuthor(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-11 pr-4 py-3 text-sm text-slate-200 focus:outline-none focus:border-indigo-500 transition-colors duration-200"
                />
              </div>
            </div>

            {/* Optional Date */}
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Publication Date (Optional)</label>
              <div className="relative">
                <Calendar className="absolute left-4 top-3.5 w-4 h-4 text-slate-500" />
                <input
                  type="date"
                  value={docDate}
                  onChange={(e) => setDocDate(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-11 pr-4 py-3 text-sm text-slate-200 focus:outline-none focus:border-indigo-500 transition-colors duration-200"
                />
              </div>
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={isUploading || !file}
              className={`w-full font-semibold text-sm py-3.5 rounded-xl transition-all duration-200 text-white flex items-center justify-center space-x-2 shadow-lg shadow-indigo-600/10 ${
                isUploading || !file
                  ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                  : 'bg-indigo-600 hover:bg-indigo-700 active:scale-95'
              }`}
            >
              {isUploading ? (
                <>
                  <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span>Processing Pipeline...</span>
                </>
              ) : (
                <span>Run Ingestion Pipeline</span>
              )}
            </button>
          </form>

          {/* Upload Status Card */}
          {uploadStatus && (
            <div className={`mt-5 p-4 rounded-xl border flex items-start space-x-3 ${
              uploadStatus.success
                ? 'bg-emerald-950/20 border-emerald-900/50 text-emerald-300'
                : 'bg-rose-950/20 border-rose-900/50 text-rose-300'
            }`}>
              {uploadStatus.success ? (
                <CheckCircle className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
              ) : (
                <AlertCircle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
              )}
              <p className="text-xs leading-relaxed">{uploadStatus.msg}</p>
            </div>
          )}
        </div>

        {/* Ingested Documents List Panel Right */}
        <div className="lg:col-span-2 bg-slate-900/30 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 shadow-xl shadow-slate-950/20">
          <h2 className="text-lg font-bold text-slate-200 mb-6 flex items-center space-x-2">
            <Database className="w-5 h-5 text-indigo-500" />
            <span>Ingested Documents Database</span>
          </h2>

          {isLoadingDocs ? (
            <div className="py-20 flex flex-col items-center justify-center space-y-3">
              <svg className="animate-spin h-8 w-8 text-indigo-500" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <p className="text-sm text-slate-500 font-mono">Syncing database files...</p>
            </div>
          ) : documents.length === 0 ? (
            <div className="py-20 text-center">
              <FileText className="w-12 h-12 text-slate-700 mx-auto mb-3" />
              <p className="text-slate-500 text-sm">No documents ingested yet.</p>
              <p className="text-slate-600 text-xs mt-1">Upload files using the portal to start index seeding.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-300">
                <thead className="bg-slate-950/60 text-slate-400 font-mono text-[10px] uppercase tracking-wider border-b border-slate-800">
                  <tr>
                    <th className="px-4 py-3.5">Filename</th>
                    <th className="px-4 py-3.5">Classification</th>
                    <th className="px-4 py-3.5">Author</th>
                    <th className="px-4 py-3.5">Ingested</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/50">
                  {documents.map((doc) => (
                    <tr key={doc.id} className="hover:bg-slate-900/40 transition-colors duration-150">
                      <td className="px-4 py-4 flex items-center space-x-3">
                        <FileText className="w-4 h-4 text-indigo-400 shrink-0" />
                        <span className="font-semibold text-slate-200 truncate max-w-[200px]" title={doc.filename}>
                          {doc.filename}
                        </span>
                      </td>
                      <td className="px-4 py-4">
                        <span className={`px-2.5 py-1 rounded-full text-[10px] font-semibold border ${
                          doc.source_type === 'interview' ? 'bg-blue-950/20 border-blue-900/50 text-blue-300' :
                          doc.source_type === 'report' ? 'bg-amber-950/20 border-amber-900/50 text-amber-300' :
                          doc.source_type === 'linkedin' ? 'bg-purple-950/20 border-purple-900/50 text-purple-300' :
                          'bg-emerald-950/20 border-emerald-900/50 text-emerald-300'
                        }`}>
                          {doc.source_type}
                        </span>
                      </td>
                      <td className="px-4 py-4 text-slate-400 truncate max-w-[120px]">
                        {doc.author || 'N/A'}
                      </td>
                      <td className="px-4 py-4 text-xs text-slate-500 font-mono">
                        {new Date(doc.created_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
