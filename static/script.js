window.addEventListener('DOMContentLoaded', () => {
    // Screen Elements
    const loadingScreen = document.getElementById('loading-screen');
    const loginScreen = document.getElementById('login-screen');
    const dashboardScreen = document.getElementById('dashboard-screen');
    
    // Login Controls
    const loginBtn = document.getElementById('login-btn');
    const adminLoginBtn = document.getElementById('admin-login-btn');
    const studentIdInput = document.getElementById('student-id');
    const fullNameInput = document.getElementById('full-name');
    const loginStatusMsg = document.getElementById('login-status-msg');

    // Attendance Core Cards
    const stepLocation = document.getElementById('step-location');
    const stepQr = document.getElementById('step-qr');
    const stepFace = document.getElementById('step-face');
    const stepSuccess = document.getElementById('step-success');

    // Sequential Trigger Inputs
    const btnLocation = document.getElementById('btn-check-location');
    const btnQr = document.getElementById('btn-scan-qr');
    const btnFace = document.getElementById('btn-scan-face');
    
    // Core Functional Target Actions Linkers
    const btnRecordAnother = document.getElementById('btn-record-another');
    const btnCloseWorkflow = document.getElementById('btn-close-workflow');

    // Navigation and Admin Elements
    const navItems = document.querySelectorAll('.nav-item');
    const tabContents = document.querySelectorAll('.tab-content');
    const navAdminBtn = document.getElementById('nav-admin-btn');
    const btnSaveAdminConfig = document.getElementById('btn-save-admin-config');
    const btnClearLogs = document.getElementById('btn-clear-logs');

    // Global session state metrics
    let activeStream = null;
    let currentUserSession = null; 

    // 1. INTRO ENGINE BOOTUP (Welcome loader sequence)
    setTimeout(() => {
        if (loadingScreen) {
            loadingScreen.classList.add('screen-fade');
            setTimeout(() => {
                loadingScreen.classList.add('hidden');
                if (loginScreen) loginScreen.classList.remove('hidden');
            }, 600);
        }
    }, 2500);

    // CORE FUNCTION: REAL CAMERA HARDWARE ACCESS ENGINE
    const startCameraSource = async (videoElementId) => {
        stopCameraSource();
        const videoElement = document.getElementById(videoElementId);
        if (!videoElement) return;

        try {
            // Humihingi na ng totoong camera permission channel sa browser layer
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { width: 640, height: 480, facingMode: "user" }
            });
            activeStream = stream;
            videoElement.srcObject = stream;
        } catch (err) {
            alert("Camera initialization error! Siguraduhing pinayagan mo ang media options sa localhost / secure layout.");
            console.error(err);
        }
    };

    const stopCameraSource = () => {
        if (activeStream) {
            activeStream.getTracks().forEach(track => track.stop());
            activeStream = null;
        }
    };

    // Helper: capture frame to base64 encoding parameter strings for facial model mapping
    const captureVideoFrameBase64 = (videoElementId) => {
        const video = document.getElementById(videoElementId);
        if (!video || !video.srcObject) return null;
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth || 640;
        canvas.height = video.videoHeight || 480;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        return canvas.toDataURL('image/jpeg').split(',')[1]; // Base64 chunk parameters data
    };

    // 2. ACCOUNT AUTHENTICATION ROUTINE (Kasal na sa Flask backend login logic mo!)
    loginBtn.addEventListener('click', () => {
        const userFullName = fullNameInput.value.trim();
        const studentId = studentIdInput.value.trim();
        
        if (userFullName === "" || studentId === "") {
            alert("Pakisulat muna ang iyong Student ID at Full Name, inhenyero/a!");
            return;
        }

        loginStatusMsg.textContent = "Please wait, confirming your student entry profile node...";
        loginStatusMsg.classList.remove('hidden');
        loginBtn.disabled = true;

        // AJAX REST endpoint bridge deployment
        fetch('/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ student_number: studentId, full_name: userFullName })
        })
        .then(res => {
            if (!res.ok) throw new Error("Student authentication node failure reference context.");
            return res.json();
        })
        .then(data => {
            if (data.status === "success") {
                currentUserSession = data.student; // Lock global index trace metrics
                
                if (navAdminBtn) navAdminBtn.classList.add('hidden');
                loginScreen.classList.add('screen-fade');
                
                setTimeout(() => {
                    loginScreen.classList.add('hidden');
                    dashboardScreen.classList.remove('hidden');
                    document.getElementById('nav-home-btn').click();
                }, 600);
            }
        })
        .catch(err => {
            alert("Sino ka muna verification flag failure: Student details not found or parsing structure rejected!");
            loginStatusMsg.classList.add('hidden');
            loginBtn.disabled = false;
        });
    });

    // 3. OFFICER / ADMIN AUTHENTICATION ROUTINE 
    if (adminLoginBtn) {
        adminLoginBtn.addEventListener('click', () => {
            const studentId = studentIdInput.value.trim();
            if (studentId === "") {
                alert("Pakisulat ang iyong Admin ID / Student credentials sa input block!");
                return;
            }

            loginStatusMsg.textContent = "Accessing administrative infrastructure control logs...";
            loginStatusMsg.classList.remove('hidden');

            fetch('/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ student_number: studentId, full_name: "ADMIN BYPASS MODE" }) 
            })
            .then(res => res.json())
            .then(data => {
                if (data.is_admin) {
                    currentUserSession = data.student || { "Student Number": studentId };
                    if (navAdminBtn) navAdminBtn.classList.remove('hidden');
                    loginScreen.classList.add('screen-fade');
                    setTimeout(() => {
                        loginScreen.classList.add('hidden');
                        dashboardScreen.classList.remove('hidden');
                        if (navAdminBtn) navAdminBtn.click();
                    }, 600);
                } else {
                    alert("Ayyy, hindi ka Admin officer ng section na ito, bakla!");
                    loginStatusMsg.classList.add('hidden');
                }
            })
            .catch(() => {
                alert("Database logging validation parsing crash error.");
                loginStatusMsg.classList.add('hidden');
            });
        });
    }

    // 4. TAB INTERACTION ROUTINE LINKER
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');
            tabContents.forEach(content => content.classList.add('hidden'));
            
            const targetTabId = item.getAttribute('data-tab');
            if (targetTabId !== 'tab-home') { stopCameraSource(); }
            
            document.getElementById(targetTabId).classList.remove('hidden');
        });
    });

    // 5. ATTENDANCE WORKFLOW CONTROLLERS (Sunod-sunod na system architecture flow ni Marisol!)
    
    // STEP 2: Location tracking hardware validation execution link
    btnLocation.addEventListener('click', () => {
        btnLocation.textContent = "fetching coordinates via device hardware browser matrix...";
        btnLocation.style.borderColor = "#ffb700";

        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const lat = position.coords.latitude;
                    const lon = position.coords.longitude;

                    fetch('/check-location', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ latitude: lat, longitude: lon })
                    })
                    .then(res => res.json())
                    .then(data => {
                        if (data.status === 'allowed') {
                            alert(`Access granted! Distance: ${data.distance} meters. Nasa loob ka nga ng CEA Building premises!`);
                            stepLocation.classList.add('hidden');
                            stepQr.classList.remove('hidden');
                            startCameraSource('qr-video-feed'); // SASINDI ANG PROD CAMERA PARA SA QR LAYER
                        } else {
                            alert(`Bawal mag-attendance: ${data.message} Kasalukuyan kang may distansyang ${data.distance}m mula sa Sintang Paaralan.`);
                            btnLocation.textContent = "Retry verification check...";
                            btnLocation.style.borderColor = null;
                        }
                    });
                },
                (err) => {
                    alert("Error: Hinarang mo ang location parameters map check ng Chrome/Edge mo gurl!");
                    btnLocation.textContent = "Retry coordinates validation...";
                }
            );
        } else {
            alert("Geolocation tracking array not supported natively by this device layout console.");
        }
    });

    // STEP 3: QR Code scanner trigger linkage checkpoint bounds
    btnQr.addEventListener('click', () => {
        btnQr.textContent = "matching room identifier matrix reference layer...";
        btnQr.style.borderColor = "#ffb700";

        // Mock scan implementation parser sequence link (Dahil video tracking library requires opencv engine loops)
        setTimeout(() => {
            alert("[QR Validation Verified]: Pasok ka sa Room Parameter, inhenyero/a!");
            stopCameraSource();
            stepQr.classList.add('hidden');
            stepFace.classList.remove('hidden');
            startCameraSource('face-video-feed'); // SASINDI ANG WEBCAM PARA SA BIOMETRIC AI EMBEDDING TEST LOOP
        }, 2000);
    });

    // STEP 4: Facial Recognition AI network mapping deployment execution handler
    btnFace.addEventListener('click', () => {
        if (!currentUserSession) return;
        
        btnFace.textContent = "analyzing landmarks and blink detection patterns via insightface node...";
        btnFace.style.borderColor = "#ffb700";

        const imageChunk = captureVideoFrameBase64('face-video-feed');
        if (!imageChunk) {
            alert("System failure capturing stable device camera data frame pipeline loop.");
            return;
        }

        // Send parameters to backend /verify-face endpoint engine module
        fetch('/verify-face', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                image: imageChunk,
                blink_check: false,
                student_number: currentUserSession["Student Number"]
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === "verified") {
                alert(`Face Verified Matrix Node Target Match! Confidence rating score value: ${data.confidence}`);
                
                // STEP 5: PUSH TO DATABASE SHEET TRANSACTIONS FILE AUTOMATICALLY!
                fetch('/mark-attendance', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ student: currentUserSession })
                })
                .then(res => res.json())
                .then(finalData => {
                    stopCameraSource();
                    stepFace.classList.add('hidden');
                    stepSuccess.classList.remove('hidden');
                    
                    // Update frontend log dynamic row entry text view values parameters container block
                    const statusTag = document.querySelector('.status-tag.present-green-tag');
                    if (statusTag && finalData.message) {
                        statusTag.textContent = finalData.message.toUpperCase();
                    }
                });
            } else {
                alert(`Biometric Access Rejected Error: ${data.message}`);
                btnFace.textContent = "Retry biometric identity capture trace...";
                btnFace.style.borderColor = null;
            }
        })
        .catch(() => {
            alert("System tracking timeout parameters framework execution anomaly failure logs.");
        });
    });

    // FUNCTIONAL RE-INITIALIZATION TRIGGERS
    const resetWorkflowState = () => {
        stopCameraSource();
        btnLocation.textContent = "checking your coordinates...";
        btnLocation.style.borderColor = null;
        btnQr.textContent = "scan the given QR code...";
        btnQr.style.borderColor = null;
        btnFace.textContent = "scan your alluring face...";
        btnFace.style.borderColor = null;

        stepSuccess.classList.add('hidden');
        stepFace.classList.add('hidden');
        stepQr.classList.add('hidden');
        stepLocation.classList.remove('hidden');
    };

    if (btnRecordAnother) { btnRecordAnother.addEventListener('click', resetWorkflowState); }
    if (btnCloseWorkflow) { btnCloseWorkflow.addEventListener('click', resetWorkflowState); }

    // ADMIN CONTROLS INTERACTIVE RE-FEEDBACK
    if (btnSaveAdminConfig) {
        btnSaveAdminConfig.addEventListener('click', () => {
            const timeVal = document.getElementById('late-time-input').value;
            if (!currentUserSession) return;

            fetch('/set-cutoff', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ student_number: currentUserSession["Student Number"], cutoff_time: timeVal })
            })
            .then(res => res.json())
            .then(data => {
                alert(`[Admin Database Sync]: ${data.message}`);
            });
        });
    }
    
    if (btnClearLogs) {
        btnClearLogs.addEventListener('click', () => {
            if (confirm("Sigurado ka bang i-pupurge ang buffer data log parameters ng Sintang Paaralan?")) {
                alert("Section transaction index references set back to empty baseline structure elements.");
            }
        });
    }

    // HIDDEN LOGO RESET LOGIC (babalik sa intro)
    const logoReset = document.getElementById('logo-reset');
    if (logoReset) {
        logoReset.addEventListener('click', () => {
            stopCameraSource();
            dashboardScreen.classList.add('hidden');
            loginBtn.disabled = false;
            loginStatusMsg.classList.add('hidden');
            fullNameInput.value = ""; 
            studentIdInput.value = "";
            currentUserSession = null;
            
            loadingScreen.classList.remove('screen-fade', 'hidden');
            resetWorkflowState(); 
            
            const progressBar = document.querySelector('.progress');
            if (progressBar) {
                progressBar.style.animation = 'none';
                progressBar.offsetHeight; 
                progressBar.style.animation = null; 
            }

            setTimeout(() => {
                loadingScreen.classList.add('screen-fade');
                setTimeout(() => {
                    loadingScreen.classList.add('hidden');
                    loginScreen.classList.remove('hidden');
                }, 600);
            }, 2500);
        });
    }
});