const exerciseLabel = document.getElementById('exercise-label');
const repsLabel = document.getElementById('reps-label');
const durationLabel = document.getElementById('duration-label')
const addLogBtn = document.getElementById('add-log')

let cardData = []


const saveToLocalStorage = function () {
      localStorage.setItem('fitify', JSON.stringify(cardData));
};

const getFromLocalStorage = function () {
      const localStorageData = JSON.parse(localStorage.getItem('fitify'));

      if (!localStorageData) return;

      localStorageData.forEach(data => cardData.push(data));
};


getFromLocalStorage();


function updateExercise(data) {
      exerciseLabel.innerText = data.exercise || 'start!!';
      repsLabel.innerText = data.rep || 0
      durationLabel.innerHTML = Math.floor((Date.now() - new Date(data.duration)) / (1000 * 60) + 330) || 0
}

function addWorkoutLog(data) {

      if (data.reps != 0) {
            cardData.push({
                  timestamp: Date.now(),
                  type: data.exercise,
                  duration: Math.floor((Date.now() - new Date(data.duration)) / (1000 * 60) + 330),
                  reps: data.rep,
                  calories: 23.2 // TODO: Implement Calorie Tracker
            })

            saveToLocalStorage();
      }

      window.location.href = '/'

}

function fetchRecognizedExercise() {
      fetch('/get_exercise')
            .then(response => response.json())
            .then(data => {
                  updateExercise(data);
            })
            .catch(error => {
                  console.error('Error fetching recognized exercise:', error);
            });
}

// Call fetchRecognizedExercise initially
fetchRecognizedExercise();

// Set an interval to fetch the recognized exercise every 1 second
setInterval(fetchRecognizedExercise, 1000);

addLogBtn.addEventListener('click', () => {
      fetch('/get_exercise')
            .then(response => response.json())
            .then(data => {
                  addWorkoutLog(data)
            })
            .catch(error => {
                  console.error('Error fetching recognized exercise:', error);
            });
})