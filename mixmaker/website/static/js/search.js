function filterBySearch() {
  // Declare variables
  var input, filter, ul, li, a, i, txtValue;
  input = document.getElementById('myInput');
  filter = input.value.toUpperCase();
  ul = document.getElementById("artists_selection");
  li = ul.getElementsByTagName('li');

  // Loop through all list items, and hide those who don't match the search query
  for (i = 0; i < li.length; i++) {
    a = li[i].getElementsByTagName("a")[0];
    txtValue = a.textContent || a.innerText;
    if (txtValue.toUpperCase().indexOf(filter) > -1) {
      // li[i].style.display = "";
      li[i].classList.remove("hidden");
    } else {

      if (Array.from(li[i].classList).includes("hidden")) {

      } else {
        li[i].classList.add("hidden");
      // li[i].style.display = "none";

      }

    }
  }
}
  
