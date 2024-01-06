from django.shortcuts import render
import subprocess
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def index(request):
    if request.method == 'POST':
        # Run your script and capture the output
        process = subprocess.Popen(
            ['python', 'D:\\DO NOT TOUCH\\bulkEmail\\swiftshare\\serverBase.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        output, errors = process.communicate()

        # Prepare the context with the script output
        context = {
            'message': "Process started successfully!",
            'output': output if output else errors  # Display errors if there's no standard output
        }
        return render(request, 'home/index.html', context)
    
    return render(request, 'home/index.html')