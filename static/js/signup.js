$(document).ready(function(){
    $("#signup-form").validate({
        rules:{
           
            username:{
                required:true,
                minlength:4
            },
            email:{
                required:true,
                email:true
            },
            password:{
                required:true,
                minlength:6
            }
        }

    })
})