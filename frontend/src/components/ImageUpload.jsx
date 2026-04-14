import React, { useState } from 'react';

export default function ImageUpload({ darkMode, onImageSelected, currentImage }) {
    const [uploading, setUploading] = useState(false);
    const [preview, setPreview] = useState(currentImage || null);

    const handleImageUpload = async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        // Check if it's an image
        if (!file.type.startsWith('image/')) {
            alert('Please upload an image file');
            return;
        }

        // Check file size (max 5MB)
        if (file.size > 5 * 1024 * 1024) {
            alert('Image size must be less than 5MB');
            return;
        }

        setUploading(true);

        try {
            // Create preview
            const reader = new FileReader();
            reader.onloadend = () => {
                setPreview(reader.result);
                onImageSelected(reader.result);
            };
            reader.readAsDataURL(file);
        } catch (error) {
            console.error('Error reading image:', error);
            alert('Failed to read image. Please try again.');
        } finally {
            setUploading(false);
        }
    };

    const handleRemoveImage = () => {
        setPreview(null);
        onImageSelected(null);
    };

    return (
        <div className="mb-6">
            <label className={`block font-semibold mb-2 ${darkMode ? 'text-gray-200' : 'text-gray-700'
                }`}>
                Upload an image (optional):
            </label>

            {preview ? (
                <div className={`border-2 rounded-lg p-4 ${darkMode ? 'border-gray-600 bg-gray-900/30' : 'border-gray-300 bg-gray-50'
                    }`}>
                    <div className="relative">
                        <img
                            src={preview}
                            alt="Preview"
                            className="max-h-64 mx-auto rounded-lg"
                        />
                        <button
                            onClick={handleRemoveImage}
                            className={`absolute top-2 right-2 p-2 rounded-full transition-colors ${darkMode
                                    ? 'bg-red-600 hover:bg-red-700 text-white'
                                    : 'bg-red-500 hover:bg-red-600 text-white'
                                }`}
                        >
                            ✕
                        </button>
                    </div>
                    <p className={`text-sm mt-2 text-center ${darkMode ? 'text-gray-400' : 'text-gray-500'
                        }`}>
                        Image will be analyzed along with text
                    </p>
                </div>
            ) : (
                <div className={`border-2 border-dashed rounded-lg p-6 text-center transition-all duration-200 ${darkMode
                        ? 'border-gray-600 hover:border-purple-500 bg-gray-900/30'
                        : 'border-gray-300 hover:border-indigo-500 bg-gray-50'
                    }`}>
                    <input
                        type="file"
                        accept="image/*"
                        onChange={handleImageUpload}
                        className="hidden"
                        id="image-upload"
                    />
                    <label
                        htmlFor="image-upload"
                        className={`cursor-pointer inline-flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${darkMode
                                ? 'bg-purple-600 hover:bg-purple-700 text-white'
                                : 'bg-indigo-600 hover:bg-indigo-700 text-white'
                            }`}
                    >
                        <span>🖼️</span>
                        <span>{uploading ? 'Uploading...' : 'Choose Image'}</span>
                    </label>
                    <p className={`mt-1 text-xs ${darkMode ? 'text-gray-500' : 'text-gray-400'}`}>
                        Multimodal analysis: Text + Image
                    </p>
                </div>
            )}
        </div>
    );
}
