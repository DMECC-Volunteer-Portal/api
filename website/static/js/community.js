$(document).ready(function () {
    fetchTopVolunteers();
});

function fetchTopVolunteers() {
    $.ajax({
        type: "GET",
        url: '/api/data/get-top-volunteers',
        xhrFields: {
            withCredentials: true
        },
        contentType: "application/json",
        success: function (response) {
            response = JSON.parse(response)
            $("#top-volunteers").empty()
            for (let key in response) {
                var entry = JSON.parse(response[key]);
                let rnk = entry['rnk'].split(/\s/).reduce((response, word) => response += word.slice(0, 1), '');
                $("#top-volunteers").append(
                    '<tr id="top-volunteer' + key + '">' +
                    '   <td class="border-b-2 pl-[2vw] whitespace-nowrap overflow-hidden">#' + key + '</td>' +
                    '   <td class="border-b-2 px-[2vw] overflow-hidden">' + entry['name'] + '</td>' +
                    '   <td class="border-b-2 px-[2vw] overflow-hidden">' + entry['school'] + '</td>' +
                    '   <td class="border-b-2 whitespace-nowrap overflow-hidden">' +
                    '       <div class="grid h-auto w-full aspect-square rounded-full border-thin text-cxs">' +
                    '           <p class="place-self-center">' + entry['org'][0] + '</p>' +
                    '       </div>' +
                    '   </td>' +
                    '   <td class="border-b-2 whitespace-nowrap overflow-hidden">' +
                    '       <div class="grid h-auto w-full aspect-square rounded-full border-thin fib fis fi-' + entry['loc'].toLowerCase() + '"></div>' +
                    '   </td>' +
                    '   <td class="border-b-2 whitespace-nowrap overflow-hidden">' +
                    '       <div class="grid h-auto w-full aspect-square rounded-full border-thin text-cxs">' +
                    '           <p class="place-self-center">' + entry['lvl'] + '</p>' +
                    '       </div>' +
                    '   </td>' +
                    '   <td class="border-b-2 whitespace-nowrap overflow-hidden">' +
                    '       <div class="grid h-auto w-full aspect-square rounded-full border-thin text-cxs">' +
                    '           <p class="place-self-center">' + rnk + '</p>' +
                    '       </div>' +
                    '   </td>' +
                    '   <td class="border-b-2 whitespace-nowrap overflow-hidden">' +
                    '       <div class="grid h-auto w-full aspect-square rounded-full border-thin text-cxs">' +
                    '           <p class="place-self-center">' + Math.round(parseInt(entry['yrs']) / 365) + '</p>' +
                    '       </div>' +
                    '   </td>' +
                    '   <td class="border-b-2 px-[2vw] whitespace-nowrap overflow-hidden">' + entry['hrs'] + '</td>' +
                    '</tr>'
                );
            }
        },
        error: function (response) {
            console.log(response)
        },
    });
}