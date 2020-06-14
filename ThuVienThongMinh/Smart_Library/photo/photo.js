 'use strict';
             const video =document.getElementById('video');
             const canvas =document.getElementById('canvas');
             const snap=document.getElementById('snap');
             const errorMsgElement = document.getElementById('span#ErrorMsg');

             const constraints ={
                audio: false,
                video:{
                    width:200,height:150
                 }
             };
             async function init(){
                try{
                    const stream =await navigator.mediaDevices.getUserMedia(constraints);
                    handleSuccess(stream);
                }
                catch(e){
                    errorMsgElement.innerHTML =`navigator.getUserMedia.error:${e.toString()}`
                }
             }
         function handleSuccess(stream){
            window.stream =stream;
            video.srcObject=stream;
         }
         init();
         var context=canvas.getContext('2d');
         snap.addEventListener("click",function(){
            context.drawImage(video,0,0,200,150);
            data=canvas.toDataURL();
            $.ajax({
                type: "POST",
                url: "saveimg.php",
                data: {
                    imgBase64: data
                }
            }).done(function (result){
                $('.booth').append('<a href="' + result + '"> Đi tới link ảnh</a>');
            });
          })


