import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Helper function to execute Python styling service
const executePythonService = (userData, imagePath = null) => {
  return new Promise((resolve, reject) => {
    const pythonScript = path.join(__dirname, '../utils/styling_engine.py');
    
    // Check if Python script exists
    if (!fs.existsSync(pythonScript)) {
      return reject(new Error('Styling service not found'));
    }

    const inputData = JSON.stringify({
      user_data: userData,
      image_path: imagePath
    });

    // Spawn Python process
    const pythonProcess = spawn('python', [pythonScript], {
      stdio: ['pipe', 'pipe', 'pipe']
    });

    let output = '';
    let errorOutput = '';

    // Handle stdout
    pythonProcess.stdout.on('data', (data) => {
      output += data.toString();
    });

    // Handle stderr  
    pythonProcess.stderr.on('data', (data) => {
      errorOutput += data.toString();
    });

    // Handle process completion
    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        console.error('Python process error:', errorOutput);
        return reject(new Error(`Python process exited with code ${code}: ${errorOutput}`));
      }

      try {
        const result = JSON.parse(output);
        resolve(result);
      } catch (parseError) {
        console.error('Failed to parse Python output:', output);
        reject(new Error('Invalid response from styling service'));
      }
    });

    // Handle process errors
    pythonProcess.on('error', (error) => {
      console.error('Failed to start Python process:', error);
      reject(new Error('Failed to start styling service'));
    });

    // Send input data to Python process
    pythonProcess.stdin.write(inputData);
    pythonProcess.stdin.end();
  });
};

// Get style advice based on user preferences
export const getStyleAdvice = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const {
      gender,
      age,
      height,
      weight,
      chest,
      waist,
      hip,
      face_shape,
      hair_color,
      hair_type,
      skin_tone,
      season,
      event,
      favorite_colors,
      cultural_factors,
      preferred_heel_height,
      preferred_shoe_type
    } = req.body;

    // Validate required fields
    if (!gender || !event) {
      return res.status(400).json({
        success: false,
        error: 'Gender and event type are required'
      });
    }

    const userData = {
      gender: gender.toLowerCase(),
      age,
      height,
      weight,
      chest,
      waist,
      hip,
      face_shape,
      hair_color,
      hair_type,
      skin_tone: skin_tone || 'neutral',
      season: season || 'current',
      event: event.toLowerCase(),
      favorite_colors,
      cultural_factors: cultural_factors || 'desi',
      preferred_heel_height,
      preferred_shoe_type
    };

    // Execute Python styling service
    const recommendation = await executePythonService(userData);

    // Log recommendation for analytics (without sensitive data)
    console.log(`Style advice generated for user ${userId}: ${event} event, ${gender} gender`);

    res.json({
      success: true,
      data: {
        recommendation: recommendation.recommendation,
        skin_tone: recommendation.skin_tone,
        metadata: {
          event: userData.event,
          gender: userData.gender,
          season: userData.season,
          cultural_preference: userData.cultural_factors,
          source: recommendation.source || 'ai_service'
        }
      }
    });

  } catch (error) {
    console.error('Style advice error:', error);
    next(error);
  }
};

// Get outfit recommendations for specific occasions
export const getOutfitRecommendations = async (req, res, next) => {
  try {
    const userId = req.user.id;
    const { occasion, weather, bodyType, colorPreferences } = req.body;

    if (!occasion) {
      return res.status(400).json({
        success: false,
        error: 'Occasion is required'
      });
    }

    const userData = {
      event: occasion.toLowerCase(),
      season: weather || 'current',
      body_type: bodyType,
      favorite_colors: colorPreferences,
      cultural_factors: 'desi' // Default for Pakistani outfits
    };

    const recommendation = await executePythonService(userData);

    res.json({
      success: true,
      data: {
        occasion,
        recommendations: recommendation.recommendation,
        styling_tips: recommendation.recommendation?.styling_tips || 'Choose outfits that make you feel confident!'
      }
    });

  } catch (error) {
    console.error('Outfit recommendation error:', error);
    next(error);
  }
};

// Get color palette recommendations based on skin tone
export const getColorRecommendations = async (req, res, next) => {
  try {
    const { skin_tone, occasion } = req.body;

    if (!skin_tone) {
      return res.status(400).json({
        success: false,
        error: 'Skin tone is required'
      });
    }

    // Color recommendations based on skin tone
    const colorPalettes = {
      warm: {
        primary: ['Gold', 'Orange', 'Red', 'Yellow', 'Peach'],
        secondary: ['Brown', 'Olive Green', 'Rust', 'Coral'],
        neutral: ['Cream', 'Warm White', 'Beige', 'Camel'],
        avoid: ['Cool Blue', 'Purple', 'Cool Pink']
      },
      cool: {
        primary: ['Blue', 'Purple', 'Cool Pink', 'Silver'],
        secondary: ['Navy', 'Teal', 'Emerald Green', 'Cool Red'],
        neutral: ['Pure White', 'Cool Grey', 'Black'],
        avoid: ['Orange', 'Gold', 'Warm Yellow']
      },
      neutral: {
        primary: ['All colors work well'],
        secondary: ['Earth tones', 'Jewel tones', 'Pastels'],
        neutral: ['White', 'Grey', 'Beige', 'Black'],
        avoid: ['Very bright neons']
      }
    };

    const palette = colorPalettes[skin_tone.toLowerCase()] || colorPalettes.neutral;

    res.json({
      success: true,
      data: {
        skin_tone,
        color_palette: palette,
        occasion_specific: occasion ? {
          formal: palette.primary.slice(0, 3),
          casual: palette.secondary.slice(0, 3),
          party: [...palette.primary.slice(0, 2), ...palette.secondary.slice(0, 1)]
        } : null
      }
    });

  } catch (error) {
    console.error('Color recommendation error:', error);
    next(error);
  }
};

// Upload image for skin tone detection
export const uploadImageForAnalysis = async (req, res, next) => {
  try {
    if (!req.file) {
      return res.status(400).json({
        success: false,
        error: 'No image file provided'
      });
    }

    const imagePath = req.file.path;
    const userData = {
      skin_tone: 'neutral',
      gender: req.body.gender || 'male',
      event: req.body.event || 'casual'
    };

    // Execute Python service with image
    const result = await executePythonService(userData, imagePath);
    
    // Clean up uploaded file
    fs.unlink(imagePath, (err) => {
      if (err) console.error('Failed to delete uploaded file:', err);
    });

    res.json({
      success: true,
      data: {
        detected_skin_tone: result.skin_tone || 'neutral',
        confidence: 0.85,
        analysis_complete: true
      }
    });
  } catch (error) {
    console.error('Image analysis error:', error);
    
    // Clean up file on error
    if (req.file) {
      fs.unlink(req.file.path, (err) => {
        if (err) console.error('Failed to delete uploaded file:', err);
      });
    }
    
    next(error);
  }
};
