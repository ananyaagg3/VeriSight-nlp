import React, { useState } from 'react';

export default function FileUpload({ darkMode, onTextExtracted }) {
    const [uploading, setUploading] = useState(false);

    const handleFileUpload = async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        setUploading(true);

        try {
            const text = await file.text();
            onTextExtracted(text);
        } catch (error) {
            console.error('Error reading file:', error);
            alert('Failed to read file. Please try again.');
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="mb-6">
            <label className={`block font-semibold mb-2 ${darkMode ? 'text-gray-200' : 'text-gray-700'
                }`}>
                Or upload a text file:
            </label>
            <div className={`border-2 border-dashed rounded-lg p-6 text-center transition-all duration-200 ${darkMode
                    ? 'border-gray-600 hover:border-purple-500 bg-gray-900/30'
                    : 'border-gray-300 hover:border-indigo-500 bg-gray-50'
                }`}>
                <input
                    type="file"
                    accept=".txt,.md"
                    onChange={handleFileUpload}
                    className="hidden"
                    id="file-upload"
                />
                <label
                    htmlFor="file-upload"
                    className={`cursor-pointer inline-flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${darkMode
                            ? 'bg-purple-600 hover:bg-purple-700 text-white'
                            : 'bg-indigo-600 hover:bg-indigo-700 text-white'
                        }`}
                >
                    <span>📁</span>
                    <span>{uploading ? 'Uploading...' : 'Choose File'}</span>
                </label>
            </div>
        </div>
    );
}
