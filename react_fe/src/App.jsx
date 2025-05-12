import { useState } from 'react'
import axios from 'axios'
import { CircularProgress, Typography, Box, Paper, Grid, Button } from '@mui/material'
import CloudUploadIcon from '@mui/icons-material/CloudUpload'
import PlayArrowIcon from '@mui/icons-material/PlayArrow'
import './App.css'

function App() {
  const [selectedFile, setSelectedFile] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [similarSongs, setSimilarSongs] = useState([])
  const [audioUrls, setAudioUrls] = useState({})
  const [uploadedFileUrl, setUploadedFileUrl] = useState(null)

  const handleFileSelect = (event) => {
    const file = event.target.files[0]
    if (file && file.type.startsWith('audio/')) {
      setSelectedFile(file)
      setError(null)
      // Create URL for the uploaded file
      const fileUrl = URL.createObjectURL(file)
      setUploadedFileUrl(fileUrl)
    } else {
      setError('Please select a valid audio file')
      setSelectedFile(null)
      setUploadedFileUrl(null)
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) return

    setIsLoading(true)
    setError(null)
    setSimilarSongs([])
    setAudioUrls({})

    const formData = new FormData()
    formData.append('file', selectedFile)

    try {
      // First API call to get similar songs
      const response = await axios.post('http://localhost:5000/api/find-similar', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      setSimilarSongs(response.data.similar_files || [])
    } catch (err) {
      setError('Error finding similar songs. Please try again.')
      console.error('Error:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const handlePlayAudio = async (songPath) => {
    if (audioUrls[songPath]) return // Audio URL already fetched

    try {
      // Second API call to get the audio file
      const response = await axios.post(`http://localhost:5000/api/audio`, {
        filename: songPath
      }, {
        responseType: 'blob'
      })

      const audioUrl = URL.createObjectURL(response.data)
      setAudioUrls(prev => ({
        ...prev,
        [songPath]: audioUrl
      }))
    } catch (err) {
      setError('Error loading audio file. Please try again.')
      console.error('Error:', err)
    }
  }

  const formatFileName = (path) => {
    // Extract just the filename without the path
    const fileName = path.split('\\').pop()
    // Remove the file extension
    return fileName.replace(/\.[^/.]+$/, "")
  }

  return (
    <Box className="app-container" sx={{ 
      maxWidth: '1200px', 
      margin: '0 auto', 
      padding: '2rem',
      minHeight: '100vh',
      backgroundColor: '#f5f5f5'
    }}>
      <Typography 
        variant="h3" 
        component="h1" 
        gutterBottom 
        sx={{ 
          textAlign: 'center',
          color: '#1a237e',
          fontWeight: 'bold',
          mb: 4
        }}
      >
        Audio Similarity Finder
      </Typography>

      <Paper 
        elevation={3} 
        sx={{ 
          p: 4, 
          mb: 4,
          borderRadius: 2,
          backgroundColor: 'white'
        }}
      >
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Box
              sx={{
                border: '2px dashed #646cff',
                borderRadius: 2,
                p: 3,
                textAlign: 'center',
                cursor: 'pointer',
                '&:hover': {
                  backgroundColor: '#f8f9fa'
                }
              }}
              component="label"
              htmlFor="audio-upload"
            >
              <input
                type="file"
                accept="audio/*"
                onChange={handleFileSelect}
                style={{ display: 'none' }}
                id="audio-upload"
              />
              <CloudUploadIcon sx={{ fontSize: 48, color: '#646cff', mb: 2 }} />
              <Typography variant="body1" sx={{ color: '#666' }}>
                {selectedFile ? selectedFile.name : 'Click to select audio file'}
              </Typography>
            </Box>
          </Grid>

          {selectedFile && (
            <Grid item xs={12} md={6}>
              <Paper elevation={2} sx={{ p: 2, borderRadius: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Uploaded File Preview
                </Typography>
                <audio
                  controls
                  src={uploadedFileUrl}
                  style={{ width: '100%' }}
                />
              </Paper>
            </Grid>
          )}
        </Grid>

        <Box sx={{ mt: 3, textAlign: 'center' }}>
          <Button
            variant="contained"
            onClick={handleUpload}
            disabled={!selectedFile || isLoading}
            sx={{
              backgroundColor: '#646cff',
              '&:hover': {
                backgroundColor: '#535bf2'
              },
              px: 4,
              py: 1.5
            }}
          >
            {isLoading ? 'Finding Similar Songs...' : 'Find Similar Songs'}
          </Button>
        </Box>
      </Paper>

      {error && (
        <Paper 
          elevation={2} 
          sx={{ 
            p: 2, 
            mb: 3, 
            backgroundColor: '#ffebee',
            color: '#c62828'
          }}
        >
          {error}
        </Paper>
      )}

      {isLoading && (
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', my: 4 }}>
          <CircularProgress sx={{ color: '#646cff' }} />
          <Typography variant="body1" sx={{ mt: 2, color: '#666' }}>
            Finding similar songs...
          </Typography>
        </Box>
      )}

      {similarSongs.length > 0 && (
        <Grid container spacing={3}>
          {similarSongs.map(([songPath, similarity], index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <Paper 
                elevation={3} 
                sx={{ 
                  p: 3,
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  borderRadius: 2
                }}
              >
                <Typography variant="h6" gutterBottom sx={{ color: '#1a237e' }}>
                  Similar Song {index + 1}
                </Typography>
                <Typography variant="body1" sx={{ mb: 1, fontWeight: 'medium' }}>
                  {formatFileName(songPath)}
                </Typography>
                <Typography 
                  variant="body2" 
                  sx={{ 
                    mb: 2,
                    color: similarity > 0.7 ? '#2e7d32' : '#ed6c02'
                  }}
                >
                  Similarity: {(similarity * 100).toFixed(2)}%
                </Typography>
                <Button
                  variant="outlined"
                  onClick={() => handlePlayAudio(songPath)}
                  startIcon={<PlayArrowIcon />}
                  sx={{ 
                    mb: 2,
                    borderColor: '#646cff',
                    color: '#646cff',
                    '&:hover': {
                      borderColor: '#535bf2',
                      backgroundColor: 'rgba(100, 108, 255, 0.04)'
                    }
                  }}
                >
                  Play Audio
                </Button>
                {audioUrls[songPath] && (
                  <audio
                    controls
                    src={audioUrls[songPath]}
                    style={{ width: '100%' }}
                  />
                )}
              </Paper>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  )
}

export default App
