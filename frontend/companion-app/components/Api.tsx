
export async function fetchData(url : string) {
    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        const data = await response.json();
        return data;
      } else {
        console.log(response)
        throw new Error('Response is not JSON');
      }
    } catch (error) {
      console.error('There was a problem with the fetch operation:', error);
      throw error;
    }
  }