   function loadbybookname(value){
         var searchtext = $('#book-search').val();
        var inpt = $('input:radio[name="search-category"]:checked');
        var category = inpt.val();
        $.ajax({
            url:'/library/booksearchbyname',
            type:'GET',
            data:{'bookid':value,'searchtext':searchtext, 'category':category},
            success: function(data){
                 $(".panel").empty();
                $(".panel").append(data);
        }

    });
    }

    $(".lend-book").click(function(){
        bookid= $(this)[0].id;
        $.ajax({
        url:'/library/bookrent/',

        data:{'bookid':bookid},
        type:'GET',
        success: function(data){
            if(data.is_added){
                swal({
                      title: "Done!",
                       text: data.success_msg,
                        type: "success"
                      },
                      function(){
                        window.location.reload();
                    });


            }
            else{

            }
        }

        });
    });

$(".action-book").click(function(){
        bookid= $(this)[0].id;
        $.ajax({
        url:'/library/adminaction/',
        data:{'bookid':bookid},
        type:'GET',
        success: function(data){
            if(data.is_added){
                        swal({
                      title: "Done!",
                       text: data.success_msg,
                        type: "success"
                      },
                      function(){
                        window.location.reload();
                    });


            }
            else{

            }
        }

        });
    });
$(".return-book").click(function(){
        bookid= $(this)[0].id;
        $.ajax({
        url:'/library/bookreturn/',
        data:{'bookid':bookid},
        type:'GET',
        success: function(data){
            if(data.is_added){
                swal({

                      title: "Done!",
                       text: data.success_msg,
                        type: "success"
                      },
                      function(){
                        window.location.reload();
                    });


            }
            else{

            }
        }

        });
    });

$('input:radio[name="search-category"]').change(function(){
    var text = $(this).val();
    var search = "Search by "+text;
    document.getElementById('book-search').placeholder= search;
});

$('#book-search').on('input', function(e){
    var searchtext = $(this).val();
    var inpt = $('input:radio[name="search-category"]:checked');
    var category = inpt.val();
    $.ajax({
        url:'/library/booksearch',
        type:'GET',
        data:{'searchtext':searchtext, 'category':category},
        success: function(data){
            bookscount = Object.keys(data).length
            $(".results").empty()
            for(var i=0; i<bookscount; i++) {
                d1 = data[i]
                bookdetail = data[i].split(",")
                $(".results").show();
                    $(".results").append('<li><a onclick=loadbybookname('+bookdetail[0]+')>'+bookdetail[1]+'<br /><span>by '+bookdetail[2]+'</span></a></li>')


            }
        }

    });
});



 $('#book-search').on('keypress', function (e) {

         if(e.which === 13){

            var searchtext = $(this).val();
        var inpt = $('input:radio[name="search-category"]:checked');
        var category = inpt.val();

        $.ajax({
            url:'/library/booksearchpage',
            type:'GET',
            data:{'searchtext':searchtext, 'category':category},
            success: function(data){
                 $(".panel").empty();
                $(".panel").append(data);
        }

    });
         }
   });

     function bookdetails(bookid){

  $.ajax(
        {
            type : "GET",
            url : '/library/detail/',
            data :{'id':bookid} ,
            success : function(data)
            {
                $("#modal_body").html(data);



              },
              error: function(XMLHttpRequest, textStatus, errorThrown) {
                $("#modal_body").html("<p style='color:red'>Oops! Something went wrong on the server. The details are below: "
                + "<br>Status : "+ textStatus + "<br>Exception : " + errorThrown + "<br><br> Please take a screenshot of this message and send it to <a href='mailto:myansrsourceHelpDesk@ansrsource.com'> MyAnsrSource Help Desk</a></p>");

              },
            }
          );
          }

          $(document).mouseup(function() {
              $(".results").hide();
          });
   function loadbypagenumber(value){
         var searchtext = $('#book-search').val();
        var inpt = $('input:radio[name="search-category"]:checked');
        var category = inpt.val();
        $.ajax({
            url:'/library/booksearchpage/',
            type:'GET',
            data:{'page':value,'searchtext':searchtext, 'category':category},
            success: function(data){
                 $(".panel").empty();
                $(".panel").append(data);
        }

    });
    }