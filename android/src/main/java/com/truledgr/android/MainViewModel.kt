package com.truledgr.android

import androidx.lifecycle.ViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.GET
import retrofit2.Response

data class UiState(
    val isLoading: Boolean = false,
    val apiMessage: String = "",
    val isError: Boolean = false
)

data class ApiResponse(
    val message: String
)

interface ApiService {
    @GET("/")
    suspend fun getRoot(): Response<ApiResponse>
}

class MainViewModel : ViewModel() {
    private val _uiState = MutableStateFlow(UiState())
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()
    
    private val apiService = Retrofit.Builder()
        .baseUrl("http://api.truledgr.app/") // Android emulator localhost
        .addConverterFactory(GsonConverterFactory.create())
        .build()
        .create(ApiService::class.java)
    
    suspend fun testApiConnection() {
        _uiState.value = _uiState.value.copy(
            isLoading = true,
            apiMessage = "",
            isError = false
        )
        
        try {
            val response = apiService.getRoot()
            if (response.isSuccessful) {
                val apiResponse = response.body()
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    apiMessage = apiResponse?.message ?: "Success!",
                    isError = false
                )
            } else {
                throw Exception("API returned error: ${response.code()}")
            }
        } catch (e: Exception) {
            _uiState.value = _uiState.value.copy(
                isLoading = false,
                apiMessage = "Cannot connect to API\n\nMake sure the backend is running on port 8000\n\nError: ${e.message}",
                isError = true
            )
        }
    }
}