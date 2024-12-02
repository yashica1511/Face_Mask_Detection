import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewImage, setPreviewImage] = useState(null);
  const [prediction, setPrediction] = useState("");

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setSelectedFile(file);
    setPrediction("");

    if (file) {
      if (!file.type.startsWith('image/')) {
        alert("Please upload a valid image file.");
        setSelectedFile(null);
        setPreviewImage(null);
        return;
      }

      const reader = new FileReader();
      reader.onload = () => {
        setPreviewImage(reader.result);
      };
      reader.readAsDataURL(file);
    } else {
      setPreviewImage(null);
    }
  };

  const handleUpload = async (file) => {
    if (!file) {
      alert("Please select a file first.");
      return;
    }

    const formData = new FormData();
    formData.append('image', file);

    try {
      console.log("Uploading file:", file.name); // Debug log
      const response = await axios.post('http://127.0.0.1:5000/predict', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      console.log('Prediction:', response.data);
      setPrediction(`${response.data.prediction} (Confidence: ${(response.data.confidence * 100).toFixed(2)}%)`);
    } catch (error) {
      console.error('Error uploading file:', error);
      alert('An error occurred while uploading the file. Please try again.');
    }
  };

  return (
    <div className="flex flex-col items-center bg-blue-700 min-h-screen text-white p-6">
      <h1 className="text-3xl font-bold mb-6">Face Mask Detection</h1>
      <div className="bg-white p-6 rounded-lg shadow-lg max-w-md w-full text-black">
        <label className="block mb-4">
          <span className="text-gray-700">Upload an Image</span>
          <input
            type="file"
            onChange={handleFileChange}
            className="mt-2 w-full text-sm p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </label>
        {previewImage && (
          <div className="mb-4">
            <img
              src={previewImage}
              alt="Preview"
              className="w-full h-auto rounded-md border"
            />
          </div>
        )}
        <button
          onClick={() => handleUpload(selectedFile)}
          className="bg-blue-700 text-white font-bold py-2 px-4 rounded w-full hover:bg-blue-800"
        >
          Predict
        </button>
      </div>

      {prediction && (
        <div className="mt-6 bg-white p-4 rounded-lg shadow-lg max-w-md w-full text-center text-black">
          <h2 className="text-lg font-semibold">Prediction:</h2>
          <p className="text-2xl font-bold text-blue-700 mt-2">{prediction}</p>
        </div>
      )}
    </div>
  );
}

export default App;
