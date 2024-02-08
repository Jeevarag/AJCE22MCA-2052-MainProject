const editForm = document.getElementById('editForm');
const selectedCountry = document.getElementById('selectedCountryText');
const selectedState = document.getElementById('selectedStateText');
const selectedCity = document.getElementById('selectedCityText');

const countrySelect = document.getElementById("country");
const stateSelect = document.getElementById("state");
const citySelect = document.getElementById("city");

editForm.addEventListener('submit', function(event){
    event.preventDefault();
    const selectedCountryText = countrySelect.options[countrySelect.selectedIndex].textContent;
    const selectedStateText = stateSelect.options[stateSelect.selectedIndex].textContent;
    const selectedCityText = citySelect.options[citySelect.selectedIndex].textContent;
    selectedCountry.value = selectedCountryText;
    selectedState.value = selectedStateText;
    selectedCity.value = selectedCityText;
    editForm.submit();
});