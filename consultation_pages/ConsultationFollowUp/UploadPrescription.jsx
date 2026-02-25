import React, { useState, useRef } from "react";
import { Modal } from "react-bootstrap";
import { toast } from "react-toastify";

const UploadPrescription = () => {
  const [showCamera, setShowCamera] = useState(false);
  const [showUploadPopup, setShowUploadPopup] = useState(false);
  const [capturedPhoto, setCapturedPhoto] = useState(null);
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const uploadRef = useRef(null);

  /* ---------------- OPEN CAMERA ---------------- */

  const openCamera = () => {
    setShowCamera(true);

    navigator.mediaDevices
      .getUserMedia({ video: true })
      .then((stream) => {
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      })
      .catch((err) => {
        console.error("Camera error:", err);
        alert("Camera not available or permission denied");
        setShowCamera(false);
      });
  };

  /* ---------------- CLOSE CAMERA ---------------- */

  const closeCamera = () => {
    if (videoRef.current?.srcObject) {
      videoRef.current.srcObject.getTracks().forEach((track) => track.stop());
      videoRef.current.srcObject = null;
    }
    setShowCamera(false);
  };

  /* ---------------- CAPTURE PHOTO ---------------- */

  const capturePhoto = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;

    if (!video || !canvas) return;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const imageData = canvas.toDataURL("image/jpeg");
    setCapturedPhoto(imageData);
    setFile(null);
    closeCamera();
  };

  /* ---------------- GALLERY ---------------- */

  const handleGalleryChange = (e) => {
    const selectedFile = e.target.files[0];
    if (!selectedFile) return;

    setLoading(true);

    setTimeout(() => {
      setFile(selectedFile);
      setLoading(false);
    }, 1000);
  };
  // Drag & Drop upload
  const handleDrop = (e) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (!droppedFile) return;

    setLoading(true);

    // simulate processing / validation
    setTimeout(() => {
      setFile(droppedFile);
      setLoading(false);
    }, 1000);
  };
  /* ---------------- CONFIRM ---------------- */
  const handleConfirm = async () => {
    if (!file) return;

    setLoading(true);

    try {
      // 👉 API call here
      // await uploadPrescription(file);

      setTimeout(() => {
        setLoading(false);
        console.log("Captured Image:", capturedPhoto);
        console.log("Uploaded File:", file);
        toast.success("Prescription uploaded successfully");
        setCapturedPhoto(false);
        setShowUploadPopup(false);
        setFile("");
        setShowUploadPopup(false);
      }, 1500);
    } catch (err) {
      setLoading(false);
    }
  };
  // const handleConfirm = () => {
  //   console.log("Captured Image:", capturedPhoto);
  //   console.log("Uploaded File:", file);
  //   alert("Prescription uploaded successfully");
  //   setCapturedPhoto(false)
  //   setShowUploadPopup(false)
  //   setFile("")
  // };

  return (
    <>
      {/* ACTION BUTTONS */}
      <div className="d-flex justify-content-center gap-3 p-3">
        <button className="btn bor-dg c-dg px-5 col-6" onClick={openCamera}>
          Camera
        </button>

        <button
          className="btn bor-dg c-dg px-5 col-6"
          onClick={() => setShowUploadPopup(true)}
        >
          Upload
        </button>
      </div>

      {showCamera && (
        <div className="modal fade show d-block" tabIndex="-1">
          <div className="modal-dialog modal-dialog-centered">
            <div className="modal-content">
              {/* Modal Header */}
              <div className="modal-header">
                <h5 className="modal-title">Camera</h5>
                <button
                  type="button"
                  className="btn-close"
                  onClick={closeCamera}
                ></button>
              </div>

              {/* Modal Body */}
              <div className="modal-body text-center">
                {!capturedPhoto && (
                  <>
                    <video
                      ref={videoRef}
                      autoPlay
                      playsInline
                      className="rounded border w-100"
                      style={{ maxWidth: "350px" }}
                    />
                    <canvas ref={canvasRef} hidden />

                    <div className="mt-3">
                      <button
                        className="btn btn-success me-2"
                        onClick={capturePhoto}
                      >
                        Capture
                      </button>

                      <button className="btn btn-danger" onClick={closeCamera}>
                        Close
                      </button>
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* IMAGE PREVIEW */}
      {capturedPhoto && (
        <div className="text-center mt-3">
          <img
            src={capturedPhoto}
            alt="Preview"
            className="img-fluid rounded"
            style={{ maxHeight: "200px" }}
          />
          <div className="mt-2">
            <button
              className="btn btn-secondary me-2"
              onClick={() => setCapturedPhoto(null)}
            >
              Retake
            </button>
            <button className="btn btn-primary" onClick={handleConfirm}>
              Confirm
            </button>
          </div>
        </div>
      )}

      {/* UPLOAD MODAL */}
      <Modal
        show={showUploadPopup}
        onHide={() => setShowUploadPopup(false)}
        centered
      >
        <Modal.Header closeButton>
          <Modal.Title>Upload Prescription</Modal.Title>
        </Modal.Header>

        <Modal.Body className="position-relative">
         {loading && (
  <div className="position-absolute top-0 start-0 w-100 h-100 d-flex flex-column justify-content-center align-items-center bg-white bg-opacity-75 z-3">
    
    <div className="w-75 mb-2">
      <div className="progress">
        <div
          className="progress-bar progress-bar-striped progress-bar-animated bg-dg"
          style={{ width: "100%" }}
        />
      </div>
    </div>

    <small className="text-muted">Processing file...</small>
  </div>
)}

          <div
            className="border border-dashed rounded p-4 text-center"
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleDrop}
            onClick={() => uploadRef.current.click()}
            style={{ cursor: "pointer" }}
          >
            <p className="mb-1">Drag & drop file here</p>
            <small className="text-muted">or click to browse</small>

            <input
              ref={uploadRef}
              type="file"
              accept="image/*,application/pdf"
              hidden
              onChange={handleGalleryChange}
            />
          </div>

          {file && !loading && (
            <p className="text-success text-center mt-3">
              Selected: <strong>{file.name}</strong>
            </p>
          )}
        </Modal.Body>

        <Modal.Footer>
          <button
            className="btn bor-dg c-dg"
            disabled={loading}
            onClick={() => setShowUploadPopup(false)}
          >
            Cancel
          </button>

          <button
            className="btn bg-dg c-w"
            disabled={!file || loading}
            onClick={handleConfirm}
          >
            {loading ? "Uploading..." : "Upload"}
          </button>
        </Modal.Footer>
      </Modal>
    </>
  );
};

export default UploadPrescription;
