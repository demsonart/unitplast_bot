/**
 * Claude Calculator Integration
 * Интеграция Claude API с кэшированием в веб-калькулятор
 *
 * Особенности:
 * - Быстрый расчет благодаря prompt caching
 * - Экономия токенов (90% на повторных запросах)
 * - Умный анализ заказов
 * - Генерация КП в один клик
 */

class ClaudeCalculator {
  constructor() {
    this.baseURL = '/api/claude';
    this.useCache = true;
    this.cacheStats = {
      totalRequests: 0,
      cachedRequests: 0,
      tokensSaved: 0
    };
  }

  /**
   * Расчет стоимости с кэшированием
   */
  async calculatePrice(material, params) {
    try {
      const response = await fetch(`${this.baseURL}/calculate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          material: material.toLowerCase(),
          params: params,
          use_cache: this.useCache
        })
      });

      const data = await response.json();

      if (data.status === 'success') {
        // Обновляем статистику кэша
        this._updateCacheStats(data.usage);
        return {
          success: true,
          price: data.result,
          usage: data.usage
        };
      } else {
        throw new Error(data.error || 'Ошибка расчета');
      }
    } catch (error) {
      console.error('Calculate error:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Анализ текста заказа
   */
  async analyzeOrder(orderText, orderHistory = null) {
    try {
      const response = await fetch(`${this.baseURL}/analyze-order`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          order_text: orderText,
          order_history: orderHistory,
          use_cache: this.useCache
        })
      });

      const data = await response.json();

      if (data.status === 'success') {
        this._updateCacheStats(data.usage);
        return {
          success: true,
          analysis: data.analysis,
          usage: data.usage
        };
      } else {
        throw new Error(data.error || 'Ошибка анализа');
      }
    } catch (error) {
      console.error('Analyze error:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Генерация коммерческого предложения
   */
  async generateProposal(orderData, companyInfo) {
    try {
      const response = await fetch(`${this.baseURL}/generate-proposal`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          order_data: orderData,
          company_info: companyInfo,
          use_cache: this.useCache
        })
      });

      const data = await response.json();

      if (data.status === 'success') {
        this._updateCacheStats(data.usage);
        return {
          success: true,
          proposal: data.proposal,
          usage: data.usage
        };
      } else {
        throw new Error(data.error || 'Ошибка генерации КП');
      }
    } catch (error) {
      console.error('Proposal error:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Проверка доступности API
   */
  async healthCheck() {
    try {
      const response = await fetch(`${this.baseURL}/health`);
      const data = await response.json();
      return data.status === 'ok';
    } catch (error) {
      console.error('Health check failed:', error);
      return false;
    }
  }

  /**
   * Обновление статистики кэша
   */
  _updateCacheStats(usage) {
    this.cacheStats.totalRequests++;

    if (usage.cache_read_input_tokens > 0) {
      this.cacheStats.cachedRequests++;
      // Примерно 90% экономии на кэшированных токенах
      this.cacheStats.tokensSaved += usage.cache_read_input_tokens * 0.9;
    }
  }

  /**
   * Получить статистику
   */
  getStats() {
    return {
      ...this.cacheStats,
      cacheHitRate: this.cacheStats.totalRequests > 0
        ? (this.cacheStats.cachedRequests / this.cacheStats.totalRequests * 100).toFixed(1) + '%'
        : 'N/A'
    };
  }

  /**
   * Включить/выключить кэширование
   */
  setUseCache(enabled) {
    this.useCache = enabled;
  }

  /**
   * Экспорт КП в PDF (интеграция с внешним сервисом)
   */
  async exportProposalPDF(proposal, filename = 'proposal.pdf') {
    // Это можно расширить для реального экспорта PDF
    // На данный момент копирует в буфер обмена
    try {
      await navigator.clipboard.writeText(proposal);
      console.log('КП скопирована в буфер обмена');
      return { success: true };
    } catch (error) {
      console.error('Export error:', error);
      return { success: false, error: error.message };
    }
  }
}

// Создать глобальный экземпляр
const claudeCalculator = new ClaudeCalculator();

// Проверить доступность при загрузке
document.addEventListener('DOMContentLoaded', async () => {
  const isHealthy = await claudeCalculator.healthCheck();
  console.log('Claude API is', isHealthy ? 'available ✅' : 'unavailable ❌');
});

/**
 * Пример использования в HTML:
 *
 * <button onclick="calculateWithClaude()">Рассчитать с Claude</button>
 *
 * async function calculateWithClaude() {
 *   const result = await claudeCalculator.calculatePrice('plastic', {
 *     height: 200,
 *     width: 150,
 *     thickness: 2,
 *     quantity: 100
 *   });
 *
 *   if (result.success) {
 *     console.log('Результат:', result.price);
 *     console.log('Статистика кэша:', claudeCalculator.getStats());
 *   }
 * }
 */
