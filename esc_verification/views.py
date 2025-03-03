from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from decouple import Config, RepositoryEnv
from .models import Otp

class EmailOtpCreateView(APIView):

    def send_email(self, email, otp):
        message = Mail(
            from_email='sclera.prog@gmail.com',
            to_emails=f'{email}',
            subject='OTP VERIFICATION SWAPCHAIN',
            html_content=f'<strong> Your Verification code is {otp}</strong>')
        try:
            file_path = "/media/alastor/New Volume/EcoSwapChain/ESC-Backend/esc-server-mint/ecoswapchain/configure .env"
            env_config = Config(RepositoryEnv(file_path))
            sg = SendGridAPIClient(env_config.get('SENDGRID_API_KEY'))
            response = sg.send(message)
            return response.status_code
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return None

    def post(self, request):
        try:
            email = request.data.get('email')
            if not email:
                raise ValueError("Email is required")
            
            if Otp.objects.filter(email=email).exists():
                Otp.objects.filter(email=email).delete()
            
            otp = Otp.objects.create(email=email)
            otp.generate()
            otp.save()

            # status_code = self.send_email(otp.email, otp.code
            
            status_code = 202
                    
            print(otp.code)

            if status_code == 202:  # SendGrid returns 202 for successfully queued emails
                return Response({"message": "OTP sent successfully"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": "Failed to send OTP"}, status=status.HTTP_400_BAD_REQUEST)

        except ValueError as ve:
            return Response({"error": str(ve)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return Response(
                {"error": "An unexpected error occurred while processing your request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class EmailOtpVerifyView(APIView):

    """
    View to verify the OTP provided by the user.
    """

    def post(self, request):
        try:
            # Retrieve OTP and email from request data
            otp = request.data.get('otp')
            email = request.data.get('email')

            # Check if both OTP and email are provided
            if not otp or not email:
                return Response({"error": "OTP and email are required"}, status=status.HTTP_400_BAD_REQUEST)

            # Fetch the OTP record for the given email
            saved_otp = Otp.objects.get(email=email)
            
            print(otp)
            # Check if the provided OTP matches the saved OTP
            if int(otp) == int(saved_otp.code):
                # Verification successful
                return Response({"success": "Verification successful"}, status=status.HTTP_202_ACCEPTED)
            else:
                # OTP doesn't match
                return Response({"message": "Verification Failed"}, status=status.HTTP_406_NOT_ACCEPTABLE)

        except Otp.DoesNotExist:
            # Email not found in the database
            return Response({"message": "OTP record for this email does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
        except ValueError:
            # In case OTP is not an integer or there’s an error converting
            return Response({"message": "Invalid OTP format"}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            # Generic exception handling for unexpected errors
            print(f"Unexpected error: {str(e)}")
            return Response({"message": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)