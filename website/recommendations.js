let series = {
  "id":"76827d5e-30e5-4d54-be68-102cd4366853",
  "title":"\"Hitokiri\" Girl Becomes Bodyguard for Duke's Daughter",
  "cover":"https://mangadex.org/covers/76827d5e-30e5-4d54-be68-102cd4366853/696bf46a-7cb1-4241-923e-abb4f5dd1427.jpg"
}


/** 
 * Display the recommendations for a given target ("series or oneshots").
 **/
function recommendations(target){
  let recommendations = [series, series, series, series, series, series, series, series,];
  recommendations.forEach((series) => {
    $("#" + target).append(`<a href=\"https://mangadex.org/title/${series.id}\">` +
      "<div class=\"recommendation-item\">"  +
        "<span>" +
          `<img src="${series.cover}" width="56" height="80"/>` +
        "</span>" +
        "<span>" +
          series.title +
        "</span>" +
    " </div>" +
   " </a>");
  });
}

/** 
 * Display previous recomendations for the user to indicate "like" or "dislike".
 **/
function rateSuggestions(){
  let previous_recommendations = [series, series, series, series, series, series, series, series,]
  $("#replaceButton").click(function(){
    $("#oldElement").replaceWith("<div>" +
      "<span>LIKE</span>" +
      "<span>DISLIKE</span>" +
    "</div>"
    );
  })
} 


// Need an AJAX backend on a python server
