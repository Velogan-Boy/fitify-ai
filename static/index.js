'use strict';

const btnWorkout = document.querySelector('.btn-workout');
const WorkoutForm = document.getElementById('workoutform');
const inputType = document.getElementById('type');
const inputDuration = document.getElementById('duration');
const changingField = document.querySelector('.changing-field');
let inputDistance;
let inputReps;

const cardContainer = document.querySelector('.card-container');

let cardData = [];
const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

//Calories consts
const cyclingCalorie = 48; //per km
const joggingCalorie = 60; //per km
const pushupsCalorie = 0.6; //per reps
const squatsCalorie = 0.32; //per reps

//////////////////////////////////

const getEnteredData = function () {
      let tempObj;
      const type = inputType.value;
      const duration = +inputDuration.value;
      let timestamp = new Date(Date.now());
      timestamp = timestamp.getTime();

      if (type === 'cycling' || type === 'jogging') {
            inputDistance = document.getElementById('distance');
            const distance = +inputDistance.value;
            tempObj = { timestamp, type, duration, distance };
      }

      if (type === 'pushups' || type === 'squats') {
            inputReps = document.getElementById('reps');
            const reps = +inputReps.value;
            tempObj = { timestamp, type, duration, reps };
      }

      cardData.push(tempObj);

      return tempObj;
};

const calcCaloriesBurnt = function (obj) {
      let calories;
      if (obj.type === 'cycling') {
            calories = obj.distance * cyclingCalorie;
      }

      if (obj.type === 'jogging') {
            calories = obj.distance * joggingCalorie;
      }

      if (obj.type === 'pushups') {
            calories = obj.reps * pushupsCalorie;
      }

      if (obj.type === 'squats') {
            calories = obj.reps * squatsCalorie;
      }

      obj.calories = calories.toFixed(2);

      return obj;
};

const resetForm = function () {
      inputDuration.value = '';

      if (inputDistance?.value) inputDistance.value = '';
      if (inputReps?.value) inputReps.value = '';
};

const addExistingCards = function () {
      cardData.forEach(card => {
            addNewCard(card);
      });
};

const addNewCard = function (card) {
      let html = `
       <div class="col-lg-3 col-md-4 col-sm-6 col-12 mb-5" data-key="${card.timestamp}">
                  <div class="card card-mod card-mod--${card.type}">
                     <div class="card-header card-header-mod">
                        <h5 class="display-4">${card.type[0].toUpperCase()}${card.type.slice(1)}</h5>
                        <div class="badge bg-light float-end text-uppercase text-dark text-mod-1">
                           <i class="far fa-calendar-alt"></i>&nbsp;
                           <span>${months[new Date(card.timestamp).getMonth()]} ${new Date(card.timestamp).getDate()}</span>
                        </div>
                     </div>

                     <ul class="list-group list-group-flush py-lg-2 text-center text-mod-1">`;


      html += `   <li class="list-group-item">
                          <i class="fas fa-dumbbell"></i>&nbsp; Reps :
                           <span class="badge badge-pill bg-dark bg-opacity-75 ms-3"><span>${card.reps}</span>  reps </span>
                        </li>
                        `;

      html += `
      <li class="list-group-item">
            <i class="far fa-clock"></i>&nbsp; Duration :
            <span class="badge badge-pill bg-dark bg-opacity-75 ms-3"><span>${card.duration}</span> mins </span>
      </li>
                        
      <li class="list-group-item">
            <i class="fas fa-fire-alt"></i>&nbsp; Calories :
            <span class="badge badge-primary badge-pill bg-warning ms-3 text-black">${card.calories} cal </span>
      </li>
      </ul>

      <div class="card-footer">
            <button class="btn btn-outline-danger btn-del float-start"  title="Delete" onclick="deleteCard(this)">
                  <i class="fas fa-ban"></i>
            </button>
            <button class="btn btn-primary btn-edit float-end"  title="Edit" onclick="editCard(this)">
                  <i class="fas fa-pencil-alt"></i>
            </button>
      </div>
       </div>
      </div>      
      `;

      cardContainer.insertAdjacentHTML('beforeend', html);
      saveToLocalStorage();
};
const editCard = function (e) {
      e.childNodes[1].classList.remove('fa-pencil-alt');
      e.childNodes[1].classList.add('fa-check');
      e.setAttribute('onclick', 'editSubmitCard(this)');

      e.parentNode.parentNode.childNodes[3].childNodes[1].childNodes[3].childNodes[0].setAttribute('contenteditable', true);
      e.parentNode.parentNode.childNodes[3].childNodes[3].childNodes[3].childNodes[0].setAttribute('contenteditable', true);

      e.parentNode.parentNode.childNodes[3].childNodes[1].childNodes[3].childNodes[0].focus();
};

const editSubmitCard = function (e) {
      e.childNodes[1].classList.remove('fa-check');
      e.childNodes[1].classList.add('fa-pencil-alt');
      e.setAttribute('onclick', 'editCard(this)');

      e.parentNode.parentNode.childNodes[3].childNodes[1].childNodes[3].childNodes[0].setAttribute('contenteditable', false);
      e.parentNode.parentNode.childNodes[3].childNodes[3].childNodes[3].childNodes[0].setAttribute('contenteditable', false);

      const targetKey = e.closest('.col-lg-3').dataset.key;

      cardData.forEach(function (card) {
            if (card.timestamp === +targetKey) {
                  if (card.distance) {
                        card.distance = e.parentNode.parentNode.childNodes[3].childNodes[1].childNodes[3].childNodes[0].textContent;
                  }

                  if (card.reps) {
                        card.reps = e.parentNode.parentNode.childNodes[3].childNodes[1].childNodes[3].childNodes[0].textContent;
                  }

                  card.duration = e.parentNode.parentNode.childNodes[3].childNodes[3].childNodes[3].childNodes[0].textContent;
                  calcCaloriesBurnt(card);
            }
      });

      saveToLocalStorage();
};

const deleteCard = function (e) {
      const targetKey = e.closest('.col-lg-3').dataset.key;
      cardData = cardData.filter(card => card.timestamp !== +targetKey);

      saveToLocalStorage();
      e.closest('.col-lg-3').remove();
};

const saveToLocalStorage = function () {
      localStorage.setItem('fitify', JSON.stringify(cardData));
};

const getFromLocalStorage = function () {
      const localStorageData = JSON.parse(localStorage.getItem('fitify'));

      if (!localStorageData) return;

      localStorageData.forEach(data => cardData.push(data));

      addExistingCards();
};

///////////////////////////////////
window.addEventListener('load', getFromLocalStorage);

btnWorkout.addEventListener('click', function () {
      window.scrollTo(0, 0);
});


