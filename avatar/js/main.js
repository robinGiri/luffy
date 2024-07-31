document.addEventListener("DOMContentLoaded", startGame);

// Global BabylonJS Variables
var canvas = document.getElementById("renderCanvas");
var engine = new BABYLON.Engine(canvas, true, { stencil: false }, true);
var scene = createScene(engine, canvas);
var camera = new BABYLON.ArcRotateCamera(
  "camera",
  BABYLON.Tools.ToRadians(-90),
  BABYLON.Tools.ToRadians(75),
  2,
  BABYLON.Vector3.Zero(),
  scene
);
var dirLight = new BABYLON.DirectionalLight(
  "dirLight",
  new BABYLON.Vector3(0, 0, 0),
  scene
);
var hemiLight = new BABYLON.HemisphericLight(
  "hemiLight",
  new BABYLON.Vector3(0, 1, 0),
  scene
);
var shadowGenerator = new BABYLON.ShadowGenerator(1024, dirLight, true);
var videoTexture = new BABYLON.VideoTexture(
  "vidtex",
  "./resources/videos/video.mp4",
  scene,
  true,
  true
);
startBTPressed();
let isFirstLoad = true;
var hdrTexture;
var hdrRotation = 0;
var idle1, idle2, idle3;
var talking1, talking2, talking3;
var salute;
var observer1, observer2, observer3;
var currentAnimation;
var talking;
var animationOffset = 50;

// Player
var player;
var modelName = "player";

// Morph Targets
var leftEye, rightEye;
var morphMultiplier_1 = 0.65;
var morphMultiplier_2 = 1;

var paused = false;
var timer = 0;

var music, sfx1, speech;
var myAnalyser;
let detectedUsers = [];

const SpeechRecognition =
  window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();
recognition.continuous = true;
recognition.interimResults = false;
recognition.lang = "en-US";

const micButton = document.getElementById("micButton");
const audioElement = document.getElementById("audioElement");
let isListening = false;

micButton.addEventListener("click", () => {
  if (isListening) {
    stopListening();
  } else {
    startListening();
  }
});

const startListening = () => {
  isListening = true;
  micButton.classList.add("listening");
  recognition.start();
};

const stopListening = () => {
  isListening = false;
  micButton.classList.remove("listening");
  recognition.stop();
};

recognition.onresult = (event) => {
  const transcript = Array.from(event.results)
    .map((result) => result[0].transcript)
    .join("");
  console.log("Transcript:", transcript);
  sendInput(transcript);
};

recognition.onerror = (event) => {
  console.error("Speech recognition error:", event.error);
  if (event.error === "no-speech" || event.error === "audio-capture") {
    stopListening();
  }
};

recognition.onend = () => {
  if (isListening) {
    recognition.start();
  }
};
let previousResponse = null;

// const fetchSightings = async () => {

//   try {
//       const response = await fetch('http://127.0.0.1:8000/api/update_sightings/');
//       if (!response.ok) {
//           throw new Error('Network response was not ok ' + response.statusText);
//       }
//       const data = await response.json();
//       setSightings(data);
//   } catch (error) {
//       setError(error.message);
//   } finally {
//       setLoading(false);
//   }
// };

// async function fetchDetectedUsers() {
//   try {
//     const response = await fetch("http://127.0.0.1:8000/api/get_sightings/");
//     if (!response.ok) {
//       throw new Error("Network response was not ok " + response.statusText);
//     }
//     const data = await response.json();
//     console.log("Detected Users:", data);
//     detectedUsers = data.detected_users || []; // Update the global detectedUsers array
//     return data;
//   } catch (error) {
//     console.error("Error fetching detected users:", error);
//     return null;
//   }
// }

// setInterval(fetchDetectedUsers, 1000);

// api.js
// async function fetchLatestSightingName() {
//   try {
//     const response = await fetch("http://127.0.0.1:8000/api/get_sightings/");
//     if (!response.ok) {
//       throw new Error("Network response was not ok");
//     }
//     const data = await response.json();
//     if (data.success) {
//       return data.name;
//     } else {
//       throw new Error("Error fetching name: " + data.error);
//     }
//   } catch (error) {
//     console.error("There was a problem with the fetch operation:", error);
//     throw error;
//   }
// }

const sendInput = async (input) => {
  try {
    // const username = await fetchLatestSightingName();
    const params = new URLSearchParams({
      username: "asmita",
      question: input,
    });
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 200000);

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/api/get_response/?${params.toString()}`,
        {
          method: "GET",
          signal: controller.signal,
        }
      );
      clearTimeout(timeoutId); // Clear the timeout if request completes in time

      const data = await response.json();
      console.log("server response:", data);
      const botReply = data.response;
      const audioUrl = data.audio; // Get the audio URL from the response
      console.log("Audio URL: ", audioUrl); // Log the audio URL

      if (audioUrl) {
        talk(audioUrl);
      }
    } catch (error) {
      clearTimeout(timeoutId);
      console.error("Error fetching data: ", error);
    }
  } catch (error) {
    console.error("Error fetching username: ", error);
  }
};

function talk() {
  // SFX Using HTML Audio to prevent Silence switch on mobile devices
  stopListening(); // Stop listening when avatar starts talking

  speech = new BABYLON.Sound(
    "speech",
    "http://localhost:5000/uploaded_files/output_audio.wav",
    scene,
    function () {
      // speech._audioBufferSource.playbackRate.value = 0.5;
    }
  );

  speech.onended = function () {
    console.log("End Speech");
    talking = false;
    setIdleAnimObservers();

    startListening();

    setTimeout(() => {
      // document.getElementById("client-logo").style.visibility = "visible";
      // document.getElementById("client-logo").classList.remove("fadeOut");
      // document.getElementById("client-logo").classList.add("fadeIn");

      if (timelineInterval) clearInterval(timelineInterval);
    }, 1000);
    scene.onBeforeRenderObservable.runCoroutineAsync(
      animationBlending(
        currentAnimation,
        0.7,
        idle1,
        0.7,
        false,
        0.02,
        0,
        idle1.duration,
        0.8
      )
    );
  };

  // Add Speech Sound to a SoundTrack to get the analiser data
  const speechTrack = new BABYLON.SoundTrack(scene);
  speechTrack.addSound(speech);

  // Audio Analyser
  myAnalyser = new BABYLON.Analyser(scene);
  speechTrack.connectToAnalyser(myAnalyser);
  myAnalyser.FFT_SIZE = 64;
  myAnalyser.SMOOTHING = 0.03;
  // myAnalyser.drawDebugCanvas();

  // Stop All Animations Init
  BABYLON.SceneLoader.OnPluginActivatedObservable.add(function (plugin) {
    currentPluginName = plugin.name;
    if (plugin.name === "gltf" && plugin instanceof BABYLON.GLTFFileLoader) {
      plugin.animationStartMode = BABYLON.GLTFLoaderAnimationStartMode.NONE;
    }
  });

  setTimeout(() => {
    if (!talking) {
      speech.volume = 1;
      talking = true;
      speech.play();
    }
  }, 1000);

  // RegisterBeforeRender Morph Target Mouth
  scene.registerBeforeRender(function () {
    const workingArray = myAnalyser.getByteFrequencyData();
    let jawValue = 0;

    if (talking) {
      // console.log("Frequency: " + workingArray[5] / 512);
      jawValue = (workingArray[5] / 512) * morphMultiplier_1;
    }

    scene
      .getMeshByName("Wolf3D_Head")
      .morphTargetManager.getTarget(16).influence = jawValue * 2;
    scene
      .getMeshByName("Wolf3D_Head")
      .morphTargetManager.getTarget(34).influence = jawValue;
    scene
      .getMeshByName("Wolf3D_Teeth")
      .morphTargetManager.getTarget(34).influence = jawValue;
  });
}

// Create Scene
function createScene(engine, canvas) {
  // Set Canvas & Engine //
  canvas = document.getElementById("renderCanvas");
  engine.clear(new BABYLON.Color3(0, 0, 0), true, true);
  var scene = new BABYLON.Scene(engine);
  return scene;
}

// Start Game
function startGame() {
  // Set Canvas & Engine

  var toRender = function () {
    scene.render();
  };
  engine.runRenderLoop(toRender);
  engine.clear(new BABYLON.Color3(1, 1, 0), true, true);

  // Setup Sounds
  music = new BABYLON.Sound(
    "Music",
    "./resources/sounds/music.mp3",
    scene,
    null,
    {
      loop: true,
    }
  );

  // SFX Using HTML Audio to prevent Silence switch on mobile devices
  sfx1 = document.createElement("audio");
  sfx1.preload = "auto";
  sfx1.src = "./resources/sounds/sfx1.mp3";

  // if (isFirstLoad) {
  //   speech = new BABYLON.Sound(
  //     "greeting",
  //     "http://127.0.0.1:8000/api/media/chatbot/chatapu/greetings_asmita.mp3",
  //     scene,
  //     function () {
  //       speech.play();
  //     }
  //   );

  //   // Once the greeting audio ends, set up the regular flow
  //   speech.onended = function () {
  //     isFirstLoad = false; // Update the flag
  //     setupRegularFlow();
  //   };
  // } else {
  //   setupRegularFlow();
  // }

  speech = new BABYLON.Sound(
    "speech",
    "http://localhost:5000/uploaded_files/output_audio.wav",
    scene,
    function () {
      // speech._audioBufferSource.playbackRate.value = 0.5;
    }
  );

  speech.onended = function () {
    console.log("End Speech");
    talking = false;
    setIdleAnimObservers();
    setTimeout(() => {
      // document.getElementById("client-logo").style.visibility = "visible";
      // document.getElementById("client-logo").classList.remove("fadeOut");
      // document.getElementById("client-logo").classList.add("fadeIn");

      if (timelineInterval) clearInterval(timelineInterval);
    }, 1000);
    scene.onBeforeRenderObservable.runCoroutineAsync(
      animationBlending(
        currentAnimation,
        0.7,
        idle1,
        0.7,
        false,
        0.02,
        0,
        idle1.duration,
        0.8
      )
    );
  };

  // Add Speech Sound to a SoundTrack to get the analiser data
  const speechTrack = new BABYLON.SoundTrack(scene);
  speechTrack.addSound(speech);

  // Audio Analyser
  myAnalyser = new BABYLON.Analyser(scene);
  speechTrack.connectToAnalyser(myAnalyser);
  myAnalyser.FFT_SIZE = 64;
  myAnalyser.SMOOTHING = 0.03;
  // myAnalyser.drawDebugCanvas();

  // Stop All Animations Init
  BABYLON.SceneLoader.OnPluginActivatedObservable.add(function (plugin) {
    currentPluginName = plugin.name;
    if (plugin.name === "gltf" && plugin instanceof BABYLON.GLTFFileLoader) {
      plugin.animationStartMode = BABYLON.GLTFLoaderAnimationStartMode.NONE;
    }
  });

  // Glow Layer
  // var gl = new BABYLON.GlowLayer("glow", scene, {
  //     mainTextureFixedSize: 256,
  //     blurKernelSize: 128
  // });
  // gl.intensity = 0.7;

  // Create Camera
  createCamera();

  // Hemispheric Light
  hemiLight.intensity = 0.15;

  // Directional Light
  dirLight.intensity = 1.75;
  dirLight.position = new BABYLON.Vector3(0, 30, 10);
  dirLight.direction = new BABYLON.Vector3(-2, -7, -5);
  dirLight.shadowMinZ = -100;
  dirLight.shadowMaxZ = 100;

  // Create Lights Transform Node
  var lightsNode = new BABYLON.TransformNode("_Lights_", scene);
  hemiLight.parent = lightsNode;
  dirLight.parent = lightsNode;

  // Setup Lighting & Import Models
  setLighting();
  // importBaseModel("base.glb");
  importAnimationsAndModel(modelName + ".glb");

  // Check Window Blur / Focus
  setInterval(checkWindowFocused, 500);

  // scene.debugLayer.show({embedMode: true}).then(function () {
  // });
}

// Check Window Focus
function checkWindowFocused() {
  if (document.hasFocus()) {
    paused = false;
    if (talking) speech.setVolume(1);
    if (timer > 2 && !music.isPlaying) {
      music.play();
    }
  } else {
    paused = true;
    speech.setVolume(0);
    if (music && music.isPlaying) {
      music.pause();
    }
  }
}

// Create ArcRotateCamera
function createCamera() {
  camera.position.z = 10;
  camera.setTarget(new BABYLON.Vector3(0, 1.5, 0));
  camera.allowUpsideDown = false;
  camera.panningSensibility = 0;
  camera.lowerRadiusLimit = 1.5;
  camera.upperRadiusLimit = 16;
  camera.lowerBetaLimit = 0.75;
  camera.upperBetaLimit = Math.PI / 2;
  camera.panningSensibility = 0;
  camera.pinchDeltaPercentage = 0.0006;
  camera.wheelPrecision = 60;
  camera.useBouncingBehavior = false;
  camera.alpha = 1.57;
  camera.beta = 1.42;
  camera.radius = 1.5;
}

async function importBaseModel(model) {
  const result = await BABYLON.SceneLoader.ImportMeshAsync(
    null,
    "./resources/models/",
    model,
    scene
  );
  const cloudsAnim = scene.getAnimationGroupByName("clouds_anim");
  const lightingTextureCache = {};

  // Add ShadowCaster to Spheres
  // shadowGenerator.addShadowCaster(sphere1);
  // shadowGenerator.addShadowCaster(sphere2);

  // Start Clouds Animations
  cloudsAnim.speedRatio = 0.2;
  cloudsAnim.play(true);

  // Setup Video Texture
  // tvMaterial.albedoTexture = videoTexture;
  // tvMaterial.emissiveTexture = videoTexture;
  // tvMaterial.emissiveColor = new BABYLON.Color3(0.1, 0.1, 0.1);
  // tvMaterial.roughness = 0.2;
  videoTexture.video.pause();

  result.meshes.forEach((mesh) => {
    const meshName = mesh.name;
    const { material } = mesh;

    mesh.isPickable = false;

    if (meshName.includes("Base")) {
      const lightmapPath =
        "./resources/textures/" + mesh.parent.name + "_lighting.jpg";

      let lightmap = lightingTextureCache[lightmapPath];
      if (!lightmap) {
        lightmap = new BABYLON.Texture(lightmapPath);
        lightingTextureCache[lightmapPath] = lightmap;
      }

      material.lightmapTexture = lightmap;
      material.useLightmapAsShadowmap = true;
      material.lightmapTexture.uAng = Math.PI;
      material.lightmapTexture.level = 1.6;
      material.lightmapTexture.coordinatesIndex = 1;

      if (meshName.includes("Base_primitive0")) {
        material.albedoColor = new BABYLON.Color3(0.99, 0.99, 0.99);
        material.metallic = 0.6;
        material.roughness = 0.6;
        material.specular = new BABYLON.Color3(0, 0, 0);
        material.specularColor = new BABYLON.Color3(0, 0, 0);
        mesh.receiveShadows = true;
      }
      if (meshName.includes("Base_primitive1")) {
        material.roughness = 0.3;
        mesh.receiveShadows = true;
      }
    }
  });
}

// Setup Animations & Player
var animationsGLB = [];

// Import Animations and Model
async function importAnimationsAndModel(model) {
  const animationPromises = [
    importAnimations("/masculine/idle/M_Standing_Idle_Variations_001.glb"),
    importAnimations("/masculine/idle/M_Standing_Idle_Variations_002.glb"),
    importAnimations("/masculine/idle/M_Standing_Idle_Variations_003.glb"),
    importAnimations("masculine/expression/M_Standing_Expressions_013.glb"),
    importAnimations("masculine/expression/M_Talking_Variations_005.glb"),
    importAnimations("masculine/expression/M_Talking_Variations_006.glb"),
    importAnimations("masculine/expression/M_Talking_Variations_007.glb"),

    importAnimations("/masculine/idle/F_Standing_Idle_Variations_001.glb"),
    importAnimations("/masculine/idle/F_Standing_Idle_Variations_002.glb"),
    importAnimations("masculine/expression/F_Talking_Variations_001.glb"),
    importAnimations("masculine/expression/F_Talking_Variations_002.glb"),
    importAnimations("masculine/expression/F_Talking_Variations_003.glb"),
    importAnimations("masculine/expression/F_Talking_Variations_004.glb"),
    // importAnimations("masculine/idle/final_thinking.glb"),
  ];

  await Promise.all(animationPromises);
  importModel(model);
}

// Import Animations
function importAnimations(animation) {
  return BABYLON.SceneLoader.ImportMeshAsync(
    null,
    "./resources/models/animations/" + animation,
    null,
    scene
  ).then((result) => {
    result.meshes.forEach((element) => {
      if (element) {
        element.dispose();
      }
    });
    animationsGLB.push(result.animationGroups[0]);
  });
}

// Import Model
function importModel(model) {
  return BABYLON.SceneLoader.ImportMeshAsync(
    null,
    "./resources/models/" + model,
    null,
    scene
  ).then((result) => {
    const player = result.meshes[0];
    player.name = "_Character_";
    shadowGenerator.addShadowCaster(result.meshes[0]);

    const modelTransformNodes = player.getChildTransformNodes();

    animationsGLB.forEach((animation) => {
      const modelAnimationGroup = animation.clone(
        model.replace(".glb", "_") + animation.name,
        (oldTarget) => {
          return modelTransformNodes.find(
            (node) => node.name === oldTarget.name
          );
        }
      );
      animation.dispose();
    });

    // Clean Imported Animations
    animationsGLB = [];

    // Setup Idle Anims
    const modelName = model
      .substring(model.lastIndexOf("/") + 1)
      .replace(".glb", "");
    idle1 = scene.getAnimationGroupByName(
      modelName + "_F_Standing_Idle_Variations_001"
    );
    idle2 = scene.getAnimationGroupByName(
      modelName + "_F_Standing_Idle_Variations_002"
    );
    idle3 = scene.getAnimationGroupByName(
      modelName + "_M_Standing_Idle_Variations_003"
    );

    talking1 = scene.getAnimationGroupByName(
      modelName + "_F_Talking_Variations_001"
    );
    talking2 = scene.getAnimationGroupByName(
      modelName + "_F_Talking_Variations_002"
    );
    talking3 = scene.getAnimationGroupByName(
      modelName + "_F_Talking_Variations_003"
    );
    salute = scene.getAnimationGroupByName(
      modelName + "_F_Standing_Expressions_004"
    );

    // Current Anim
    currentAnimation = idle1;
    idle1.play(false);

    setIdleAnimObservers();

    setReflections();
    setShadows();
    currentAnimation = scene.animationGroups[0];
    showButtonHide();

    leftEye = scene
      .getMeshByName("Wolf3D_Head")
      .morphTargetManager.getTarget(50);
    rightEye = scene
      .getMeshByName("Wolf3D_Head")
      .morphTargetManager.getTarget(51);

    console.log(scene.getMeshByName("Wolf3D_Head").morphTargetManager);

    // Setup Init Jaw Forward
    scene
      .getMeshByName("Wolf3D_Head")
      .morphTargetManager.getTarget(9).influence = 0.4;

    // Animate Face Morphs
    animateFaceMorphs();
  });
}

// Animate Eyes
function wait(ms) {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
}

// Animate Face Morphs using intervals
function animateFaceMorphs() {
  const mesh = scene.getMeshByName("Wolf3D_Head");

  const getRandomNumber = (min, max) =>
    Math.floor(Math.random() * (max - min + 1)) + min;
  // Animate Eyes
  const animateEyes = async () => {
    const randomNumber = getRandomNumber(1, 2);
    if (randomNumber === 1) {
      leftEye.influence = 1;
      rightEye.influence = 1;
      await wait(100);
      leftEye.influence = 0;
      rightEye.influence = 0;
      const randomNumber2 = getRandomNumber(1, 2);
      if (randomNumber2 === 1) {
        await wait(100);
        leftEye.influence = 1;
        rightEye.influence = 1;
        await wait(100);
        leftEye.influence = 0;
        rightEye.influence = 0;
      }
    }
  };

  // animateMorphTarget registerBeforeRender
  const animateMorphTarget = (
    targetIndex,
    initialValue,
    targetValue,
    numSteps
  ) => {
    let currentStep = 0;
    const morphTarget = mesh.morphTargetManager.getTarget(targetIndex);

    const animationCallback = () => {
      currentStep++;
      const t = currentStep / numSteps;
      morphTarget.influence = BABYLON.Scalar.Lerp(initialValue, targetValue, t);
      if (currentStep >= numSteps) {
        scene.unregisterBeforeRender(animationCallback);
      }
    };

    scene.registerBeforeRender(animationCallback);
  };

  // Brows
  const animateBrow = () => {
    const random = Math.random() * 0.8;
    const initialValue = mesh.morphTargetManager.getTarget(2).influence;
    const targetValue = random;
    animateMorphTarget(2, initialValue, targetValue, 15);
    animateMorphTarget(3, initialValue, targetValue, 15);
    animateMorphTarget(4, initialValue, targetValue, 15);
  };

  // Smile
  const animateSmile = () => {
    const random = Math.random() * 0.18 + 0.02;
    const initialValue = mesh.morphTargetManager.getTarget(47).influence;
    const targetValue = random;
    animateMorphTarget(47, initialValue, targetValue, 30);
    animateMorphTarget(48, initialValue, targetValue, 30);
  };

  // Mouth Left / Right
  const animateMouthLeftRight = () => {
    const random1 = Math.random() * 0.7;
    const randomLeftOrRight = getRandomNumber(0, 1);
    const targetIndex = randomLeftOrRight === 1 ? 22 : 21;
    const initialValue =
      mesh.morphTargetManager.getTarget(targetIndex).influence;
    const targetValue = random1;
    animateMorphTarget(targetIndex, initialValue, targetValue, 90);
  };

  // Nose
  const animateNose = () => {
    const random = Math.random() * 0.7;
    const initialValue = mesh.morphTargetManager.getTarget(17).influence;
    const targetValue = random;
    animateMorphTarget(17, initialValue, targetValue, 60);
    animateMorphTarget(18, initialValue, targetValue, 60);
  };

  // Jaw Forward
  const animateJawForward = () => {
    const random = Math.random() * 0.5;
    const initialValue = mesh.morphTargetManager.getTarget(9).influence;
    const targetValue = random;
    animateMorphTarget(9, initialValue, targetValue, 60);
  };

  // Cheeks
  const animateCheeks = () => {
    const random = Math.random() * 1;
    const initialValue = mesh.morphTargetManager.getTarget(32).influence;
    const targetValue = random;
    animateMorphTarget(32, initialValue, targetValue, 60);
    animateMorphTarget(33, initialValue, targetValue, 60);
  };

  setInterval(animateEyes, 800);
  setInterval(animateBrow, 1200);
  setInterval(animateSmile, 2000);
  setInterval(animateMouthLeftRight, 1500);
  setInterval(animateNose, 1000);
  setInterval(animateJawForward, 2000);
  setInterval(animateCheeks, 1200);
}

// Setup Idle Animation OnEnd Observers
function setIdleAnimObservers() {
  observer1 = idle1.onAnimationEndObservable.add(function () {
    scene.onBeforeRenderObservable.runCoroutineAsync(
      animationBlending(idle1, 0.8, idle2, 0.8, false, 0.02)
    );
  });
  observer2 = idle2.onAnimationEndObservable.add(function () {
    scene.onBeforeRenderObservable.runCoroutineAsync(
      animationBlending(idle2, 0.8, idle3, 0.8, false, 0.02)
    );
  });
  observer3 = idle3.onAnimationEndObservable.add(function () {
    scene.onBeforeRenderObservable.runCoroutineAsync(
      animationBlending(idle3, 0.8, idle1, 0.8, false, 0.02)
    );
  });
}

// Remove Idle Animation OnEnd Observers
function removeAnimObservers() {
  idle1.onAnimationEndObservable.remove(observer1);
  idle2.onAnimationEndObservable.remove(observer2);
  idle3.onAnimationEndObservable.remove(observer3);
  idle1.stop();
  idle2.stop();
  idle3.stop();
}

// Play Sounds
function playSounds() {
  sfx1.play();
  if (speech && speech.isPlaying) {
    speech.stop();
    speech.currentTime = 0;
  }
  if (music && !music.isPlaying) {
    music.volume = 0.6;
    music.play();
  }
}

// startBTPressed Function from Client Logo
var disableButton = false;
function startBTPressed() {
  talking = false;
  camera.attachControl(canvas, true);

  // playSounds();

  videoTexture.video.play();
  timer = 0;

  document.getElementById("client-logo").classList.add("fadeOut");
  setTimeout(() => {
    document.getElementById("client-logo").style.visibility = "hidden";
    startTimeline();
  }, 400);
}

// Animation Blending
function* animationBlending(
  fromAnim,
  fromAnimSpeedRatio,
  toAnim,
  toAnimSpeedRatio,
  repeat,
  speed,
  toAnimFrameIn,
  toAnimFrameOut,
  maxWeight
) {
  if (!toAnimFrameIn) toAnimFrameIn = 0;
  if (!toAnimFrameOut) toAnimFrameOut = toAnim.duration;
  if (!maxWeight) maxWeight = 1;

  let currentWeight = 1;
  let newWeight = 0;
  fromAnim.stop();
  toAnim.start(repeat, toAnimSpeedRatio, toAnimFrameIn, toAnimFrameOut, false);
  fromAnim.speedRatio = fromAnimSpeedRatio;
  toAnim.speedRatio = toAnimSpeedRatio;
  while (newWeight < maxWeight) {
    newWeight += speed;
    currentWeight -= speed;
    toAnim.setWeightForAllAnimatables(newWeight);
    fromAnim.setWeightForAllAnimatables(currentWeight);
    yield;
  }
  currentAnimation = toAnim;
}

// Start Timeline
let timelineInterval;
function startTimeline() {
  clearInterval(timelineInterval);

  // // Step 1 - Camera Animation
  // const animationDuration = 250;
  // camera.alpha = 1.57;
  // camera.beta = 1.42;
  // BABYLON.Animation.CreateAndStartAnimation("cameraAnim", camera, "radius", 50, animationDuration, 15, 2.4, BABYLON.Animation.ANIMATIONLOOPMODE_RELATIVE, undefined, () => {
  //     camera.useAutoRotationBehavior = true;
  //     camera.autoRotationBehavior.idleRotationSpeed = 0.0;
  // });

  // Clear Timer
  let timer = 0;

  // Time Interval
  timelineInterval = setInterval(() => {
    timer++;

    // console.log("Timer: " + timer);
    if (timer === 1) {
      // Remove Idle Animation Observers
      removeAnimObservers();

      // Idle to Salute Anim
      scene.onBeforeRenderObservable.runCoroutineAsync(
        animationBlending(
          currentAnimation,
          1.0,
          1.0,
          false,
          0.015,
          0,
          salute.duration - animationOffset,
          1
        )
      );
    }

    // Start Speech after 3 seconds
    if (timer === 3) {
      // Start Speech
      setTimeout(() => {
        if (!talking) {
          speech.volume = 1;
          talking = true;
          speech.play();
        }
      }, 200);

      // // Show Client Card
      setTimeout(() => {
        const clientCardContainer = document.getElementById(
          "client-card-container"
        );
        if (clientCardContainer.style.visibility === "hidden") {
          // clientCardContainer.style.visibility = "visible";
          // clientCardContainer.classList.add("fadeIn");
          // clientCardContainer.classList.remove("fadeOut");
        }
      }, 800);

      // RegisterBeforeRender Morph Target Mouth
      scene.registerBeforeRender(function () {
        const workingArray = myAnalyser.getByteFrequencyData();
        let jawValue = 0;

        if (talking) {
          // console.log("Frequency: " + workingArray[5] / 512);
          jawValue = (workingArray[5] / 512) * morphMultiplier_1;
        }

        scene
          .getMeshByName("Wolf3D_Head")
          .morphTargetManager.getTarget(16).influence = jawValue * 2;
        scene
          .getMeshByName("Wolf3D_Head")
          .morphTargetManager.getTarget(34).influence = jawValue;
        scene
          .getMeshByName("Wolf3D_Teeth")
          .morphTargetManager.getTarget(34).influence = jawValue;
      });
    }

    // Check Talking Animations -- Start after 3 sec.
    if (
      talking &&
      speech.isPlaying &&
      timer >= 3 &&
      !currentAnimation.isPlaying
    ) {
      let newTalkingAnim;
      do {
        const random2 = Math.floor(Math.random() * 3) + 1;
        if (random2 === 1) newTalkingAnim = talking1;
        else if (random2 === 2) newTalkingAnim = talking2;
        else if (random2 === 3) newTalkingAnim = talking3;
      } while (newTalkingAnim === currentAnimation);
      scene.onBeforeRenderObservable.runCoroutineAsync(
        animationBlending(
          currentAnimation,
          0.8,
          newTalkingAnim,
          0.8,
          false,
          0.02,
          animationOffset,
          newTalkingAnim.duration - animationOffset,
          0.75
        )
      );
    }
  }, 1000);
}

// Environment Lighting
function setLighting() {
  hdrTexture = BABYLON.CubeTexture.CreateFromPrefilteredData(
    "./resources/env/environment_19.env",
    scene
  );
  hdrTexture.rotationY = BABYLON.Tools.ToRadians(hdrRotation);
  hdrSkybox = BABYLON.MeshBuilder.CreateBox("skybox", { size: 1024 }, scene);
  var hdrSkyboxMaterial = new BABYLON.PBRMaterial("skybox", scene);
  hdrSkyboxMaterial.backFaceCulling = false;
  hdrSkyboxMaterial.reflectionTexture = hdrTexture.clone();
  hdrSkyboxMaterial.reflectionTexture.coordinatesMode =
    BABYLON.Texture.SKYBOX_MODE;
  hdrSkyboxMaterial.microSurface = 0.5;
  hdrSkyboxMaterial.disableLighting = true;
  hdrSkybox.material = hdrSkyboxMaterial;
  hdrSkybox.infiniteDistance = true;
}

// Set Shadows
function setShadows() {
  scene.meshes.forEach(function (mesh) {
    if (mesh.name != "skybox" && mesh.name != "ground") {
      shadowGenerator.darkness = 0.4;
      shadowGenerator.bias = 0.001;
      shadowGenerator.usePercentageCloserFiltering = true;
      shadowGenerator.filteringQuality = 1;
    }
  });
}

// Set Reflections
function setReflections() {
  scene.materials.forEach(function (material) {
    if (material.name != "skybox") {
      material.reflectionTexture = hdrTexture;
      material.reflectionTexture.level = 0.9;
      material.environmentIntensity = 0.9;
      material.disableLighting = false;
    }
  });
}

// Show START DEMO BUTTON
function showButtonHide() {
  setTimeout(() => {
    document.getElementById("customBT").style.visibility = "visible";
    document.getElementById("customBT").classList.add("fadeIn");
  }, 1200);
  setPostProcessing();

  setTimeout(() => {
    optimizeScene();
  }, 2000);
}

// Hide Loading View
function hideLoadingView() {
  // Unlock Audio Engine
  BABYLON.Engine.audioEngine.unlock();
  document.getElementById("customBT").classList.add("fadeOut");
  document.getElementById("customBT").classList.remove("fadeIn");
  document.getElementById("loadingDiv").classList.add("fadeOut");
  setTimeout(() => {
    document.getElementById("loadingDiv").style.display = "none";
    document.getElementById("customBT").style.visibility = "hidden";
    document.getElementById("customBT").classList.remove("fadeIn");
    document.getElementById("customBT").classList.remove("fadeOut");
  }, 400);
}

// Optimizer
function optimizeScene() {
  scene.skipPointerMovePicking = true;
  scene.autoClear = false; // Color buffer
  scene.autoClearDepthAndStencil = false; // Depth and stencil, obviously
  scene.getAnimationRatio();
  scene.blockfreeActiveMeshesAndRenderingGroups = true;
  // Hardware Scaling
  var options = new BABYLON.SceneOptimizerOptions(30, 500);
  options.addOptimization(new BABYLON.HardwareScalingOptimization(0, 1));
  var optimizer = new BABYLON.SceneOptimizer(scene, options);
  optimizer.start();
}

// Post Processing
function setPostProcessing() {
  //return;
  var pipeline = new BABYLON.DefaultRenderingPipeline(
    "defaultPipeline", // The name of the pipeline
    false, // Do you want the pipeline to use HDR texture?
    scene, // The scene instance
    [scene.activeCamera] // The list of cameras to be attached to
  );
  pipeline.imageProcessing.exposure = 1.02; // 1 by default
  pipeline.samples = 4;
  pipeline.bloomEnabled = false;
}

// Resize Window
window.addEventListener("resize", function () {
  engine.resize();
});
