

$(document).ready(function () {
    // reset all parameters on page load


    // on selecting the country option

    $('#countries').on('change', function () {
        // since province and region is dependent 

        // on country select, emty all the options from select input

        $("#province").val("all");
        $("#region").val("all");
        send_data['province'] = '';
        send_data['region'] = '';

        // update the selected country

        if (this.value == "all")
            send_data['country'] = "";
        else
            send_data['country'] = this.value;

        //get province of selected country

        getProvince(this.value);
        // get api data of updated filters

        getAPIData();
    });

    // on filtering the variety input

    $('#variety').on('change', function () {
        // get the api data of updated variety

        if (this.value == "all")
            send_data['variety'] = "";
        else
            send_data['variety'] = this.value;
        getAPIData();
    });

    // on filtering the province input

    $('#province').on('change', function () {
        // clear the region input 

        // since it is dependent on province input

        send_data['region'] = "";
        $('#region').val("all");
        if (this.value == "all")
            send_data['province'] = "";
        else
            send_data['province'] = this.value;
        getRegion(this.value);
        getAPIData();
    });

    // on filtering the region input

    $('#region').on('change', function () {
        if (this.value == "all")
            send_data['region'] = "";
        else
            send_data['region'] = this.value;
        getAPIData();
    });

    // sort the data according to price/points

    $('#sort_by').on('change', function () {
        send_data['sort_by'] = this.value;
        getAPIData();
    });

    // display the results after reseting the filters

    $("#display_all").click(function () {
        resetFilters();
        getAPIData();
    })
})



function getSolutions() {
    // fill the options of countries by making ajax call

    // obtain the url from the countries select input attribute

    let url = $("#countries").attr("url");

    // makes request to getCountries(request) method in views

    $.ajax({
        method: 'GET',
        url: url,
        data: {},
        success: function (result) {

            countries_option = "<option value='all' selected>All Countries</option>";
            $.each(result["countries"], function (a, b) {
                countries_option += "<option>" + b + "</option>"
            });
            $("#countries").html(countries_option)
        },
        error: function (response) {
            console.log(response)
        }
    });
}

const countryLinks = document.querySelectorAll('.country-link');
console.log(countryLinks);