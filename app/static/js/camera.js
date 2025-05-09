window.Camera = class Camera {
  #currentStream;
  #streaming = false;
  #width = 640;
  #height = 0;

  #videoElement;
  #selectCameraElement;
  #canvasElement;

  #takePictureButton;

  static addNewStream(stream) {
    if (!Array.isArray(window.currentStreams)) {
      window.currentStreams = [stream];
      return;
    }
    window.currentStreams = [...window.currentStreams, stream];
  }

  static stopAllStreams() {
    if (!Array.isArray(window.currentStreams)) {
      window.currentStreams = [];
      return;
    }
    window.currentStreams.forEach((stream) => {
      if (stream.active) {
        stream.getTracks().forEach((track) => track.stop());
      }
    });
  }

  constructor({ video, cameraSelect, canvas, options = {} }) {
    this.#videoElement = video;
    this.#selectCameraElement = cameraSelect;
    this.#canvasElement = canvas;

    if (this.isProbablyLaptop()) {
      alert("Anda menggunakan laptop. Gunakan kamera dari HP untuk hasil lebih baik.");
    }

    this.#initialListener();
  }

  isProbablyLaptop() {
    return window.innerWidth > 800 || !/Android|iPhone|iPad|iPod/i.test(navigator.userAgent);
  }

  #initialListener() {
    this.#videoElement.oncanplay = () => {
      if (this.#streaming) {
        return;
      }

      this.#height = (this.#videoElement.videoHeight * this.#width) / this.#videoElement.videoWidth;
      this.#canvasElement.setAttribute('width', this.#width);
      this.#canvasElement.setAttribute('height', this.#height);

      this.#streaming = true;
    };

  }

  async #populateDeviceList(stream) {
    try {
      if (!(stream instanceof MediaStream)) {
        return Promise.reject(Error('MediaStream not found!'));
      }
      const { deviceId } = stream.getVideoTracks()[0].getSettings();
      const enumeratedDevices = await navigator.mediaDevices.enumerateDevices();
      const list = enumeratedDevices.filter((device) => {
        return device.kind === 'videoinput';
      });
      const html = list.reduce((accumulator, device, currentIndex) => {
        return accumulator.concat(`
          <option
            value="${device.deviceId}"
            ${deviceId === device.deviceId ? 'selected' : ''}
          >
            ${device.label || `Camera ${currentIndex + 1}`}
          </option>
        `);
      }, '');
      this.#selectCameraElement.innerHTML = html;
    } catch (error) {
      console.error('#populateDeviceList: error:', error);
    }
  }

  async #getStream() {
    try {
      const constraints = {
        video: {
          facingMode: { exact: "environment" },
          aspectRatio: 4 / 3
        }
      };

      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      return stream;
    } catch (error) {
      console.warn("Tidak dapat mengakses kamera belakang. Kemungkinan Anda menggunakan laptop.");
      alert("Tidak dapat mengakses kamera belakang. Gunakan perangkat mobile untuk pengalaman terbaik.");
      return null;
    }
  }

  async launch() {
    this.#currentStream = await this.#getStream();

    // Record all MediaStream in global context
    Camera.addNewStream(this.#currentStream);

    this.#videoElement.srcObject = this.#currentStream;
    this.#videoElement.play();

    this.#clearCanvas();
  }

  stop() {
    if (this.#videoElement) {
      this.#videoElement.srcObject = null;
      this.#streaming = false;
    }

    if (this.#currentStream instanceof MediaStream) {
      this.#currentStream.getTracks().forEach((track) => {
        track.stop();
      });
    }
    this.#clearCanvas();
  }

  #clearCanvas() {
    const context = this.#canvasElement.getContext('2d');
    context.fillStyle = '#AAAAAA';
    context.fillRect(0, 0, this.#canvasElement.width, this.#canvasElement.height);
  }

  async takePicture(maxWidth = 640) {
    if (!(this.#width && this.#height)) {
      return null;
    }

    // Hitung ukuran resize-nya
    let targetWidth = this.#width;
    let targetHeight = this.#height;

    if (this.#width > maxWidth) {
      targetWidth = maxWidth;
      targetHeight = Math.floor((this.#height / this.#width) * maxWidth);
    }

    this.#canvasElement.width = targetWidth;
    this.#canvasElement.height = targetHeight;

    const context = this.#canvasElement.getContext('2d');
    context.drawImage(this.#videoElement, 0, 0, targetWidth, targetHeight);

    return await new Promise((resolve) => {
      this.#canvasElement.toBlob((blob) => resolve(blob), 'image/jpeg', 0.8); // kualitas 0.8
    });
  }

  addCheeseButtonListener(selector, callback) {
    this.#takePictureButton = document.querySelector(selector);
    this.#takePictureButton.onclick = callback;
  }

}