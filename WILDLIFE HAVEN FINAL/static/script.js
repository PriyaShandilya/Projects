const video = document.getElementById("video");
const detectBtn = document.getElementById("detect-btn");
const status1 = document.getElementById("status1");

const fileInput = document.getElementById('videoInput'); 

fileInput.addEventListener("change", (event) => {
  const file = event.target.files[0];
  const filePath = URL.createObjectURL(file);
  console.log("Selected file:", file.name);
  console.log("File path:", filePath);
  video.src = filePath;
});

detectBtn.addEventListener("click", detectPoaching);

function detectPoaching() {
  if (!video.src) {
    status1.innerHTML = "Please upload a video file.";
    return;
  }
  console.log(video.src);
  status1.innerHTML = "Poaching detection in progress...";
  // Example: Simulating a detection result
  setTimeout(() => {
    status1.innerHTML = "No poaching detected.";
  }, 3000); // Assuming 3 seconds for detection
}
